import inspect
import json
import random
import typing

from datetime import datetime
from enum import Enum, IntEnum

from .http import (
  Route,
  AsyncRoute
)

if typing.TYPE_CHECKING:
  from .shape import ShapeBase


MISSING = object()

class ABCBase:
  """Base class for objects in this module
  
  .. container:: operations
  
      .. describe:: x == y
      
          Checks if the instance is same as other
          
      .. describe:: x != y
      
          Checks if the instance is not same as other

  """
  def __init__(self, id: str = MISSING):
    self.id = id

  @property
  def id(self) -> str:
    return self.__id

  @id.setter
  def id(self, value: str):
    if value is MISSING:
      value = str(random.randint(1,9))
      value += "".join(str(random.randint(0,9)) for _ in range(9))
      
    self.__id = value

  @classmethod
  def new(cls): return cls()
  
  def __eq__(self, o):
    if not hasattr(o, "id"): return False
    return self.id == o.id and self.__class__ == o.__class__

  def __ne__(self, o):
    return not self == o

class ShapeUser(ABCBase):
  """User for shape
  
  Parameters
  -----------
  id: Optional[:class:`~str`]
    ID of the user, (Randomly generated if not given)
  auth_token: Optional[:class:`~str`]
    Authorization token of user. Not required.
  """
  def __init__(self, id: str=MISSING, auth_token: str = MISSING):
    self.auth_token = auth_token
    super().__init__(id)

  @property
  def auth_token(self) -> str:
    return self.__auth_token
    
  @auth_token.setter
  def auth_token(self, token: str):
    self.__auth_token = token if token is not MISSING else None

  def auth(self, shape):
    """Used to authorise the user with shapes.inc
    
    Parameters
    -----------
    shape: Union[:class:`shapesinc.Shape`, :class:`shapesinc.AsyncShape`]
      The shape through which the user is to be authorised.
      
    Returns
    --------
    List[:class:`~str`, Callable]
      URL to authorise and authorisation function
      
    Example
    --------
    
    .. code-block:: python3
    
        user = ShapeUser("999") # Any ID
        url, authorise = user.auth(my_shape)
        print("Click on this link and authorise yourself. ", url)
        # A code will be shown on the page.
        code = input("Enter the code: ")
        # now if your shape is AsyncShape then you'd need to await the function
        await authorise(code)
        # if it isn't then you can normally proceed with
        authorise(code)

    """
    def proc(code: str):
      res = (Route/"auth/nonce").request(data=dict(
        app_id = shape.app_id,
        code = code
      ))
      self.auth_token = res["auth_token"]
      
    async def a_proc(code: str):
      res = await (AsyncRoute/"auth/nonce").request(data=dict(
        app_id = shape.app_id,
        code = code
      ))
      
      self.auth_token = res["auth_token"]
    
    meth = proc if shape.type == "SYNCHRONOUS" else a_proc
    
    return shape.auth_url, meth
    
  def send(
    self,
    shape,
    message: "Message",
    channel: "ShapeChannel" = None
  ) -> "PromptResponse":
    """Alias to `shape.prompt`
    
    Parameters
    -----------
    shape: Union[:class:`shapesinc.Shape`, :class:`shapesinc.AsyncShape`]
      Shape
    message: Union[:class:`~str`, :class:`shapesinc.Message`]
      Message
    channel: Optional[:class:`shapesinc.ShapeChannel`]
      Channel
      
    Returns
    --------
    :class:`shapesinc.PromptResponse`
      Message Response
      
    Example
    --------
    
    .. code-block:: python3
    
        user.send(my_shape, "Hi.")
        # or
        await user.send(my_shape, "Hi.")
    """
    return shape.prompt(message, user=self, channel=channel)

class ShapeChannel(ABCBase):
  """Channel for shape. Used for context
  
  Parameters
  -----------
  id: Optional[:class:`~str`]
    ID of the channel, (Randomly generated if not given)
  """


class ContentType(IntEnum):
  """Enumeration for message content.
  
  Attributes
  -----------
  text:
    for text messages
  audio:
    for audio messages
  image:
    for image messages
  """
  text:  int = 1
  audio: int = 2
  image: int = 3
  
  def __repr__(self) -> str:
    return f"<ContentType 'shapesinc.ContentType.{self.name}'>"
    
  __str__ = __repr__

class MessageContent(ABCBase):
  """Content of the message
  
  Attributes
  -----------
  content: :class:`~str`
    The content of message if it is text or its URL.
  type: :class:`shapesinc.ContentType`
  """
  def __init__(self, content: str, type: ContentType = ContentType.text):
    self.type = type
    super().__init__(content)

  @property
  def content(self) -> str:
    """Content of the message"""
    return self.id

  @content.setter
  def content(self, value: str):
    self.id = value
    
  @classmethod
  def from_dict(cls, data: dict):
    """Converts json to message content"""
    assert data["type"] in ["image_url", "audio_url", "text"], ValueError("Expected ContentType input")
    
    if data["type"]=="text":
      return cls("text", ContentType.text)
      
    return cls(
      data[data["type"]]["url"],
      ContentType.audio if data["type"] == "audio_url" else ContentType.image
    )
    
  def to_dict(self) -> dict:
    """Converts itself to JSON format"""
    return {
      "type": f"{self.type.name}_url",
      f"{self.type.name}_url": {
        "url": self.content
      }
    } if self.type != ContentType.text else {
      "type": "text",
      "text": self.content
    }
    
  def __eq__(self, o):
    if not super().__eq__(o):
      return False
    if not hasattr(o, "type"): return False
    return self.type == o.type
    
class Message:
  """Message
  
  Attributes
  -----------
  content: typing.List[:class:`shapesinc.MessageContent`]
    Contents of the message.
  role: :class:`~str`
    Role of the author. Default: "user"
  """
  def __init__(
    self,
    content: typing.List[MessageContent] = None,
    role: str = "user",
    *,
    tool_calls: typing.List[dict] = []
  ):
    assert content, ValueError("Cannot create empty message!")
    self.content = content
    self.role = role
    self.tool_calls = tool_calls or []
    
  def __repr__(self) -> str:
    if len(self.content)==1 and self.content[0].type==ContentType.text:
      return self.content[0].content
      
    return super().__repr__()
    
  __str__ = __repr__
  
  def to_dict(self) -> dict:
    """Converts itself into JSON format"""
    if len(self.content)==1 and self.content[0].type==ContentType.text:
      cont = self.content[0].content
    else:
      cont = [c.to_dict() for c in self.content]
    res = {
      "role": self.role,
      "content": cont
    }
    if self.tool_calls:
      res["tool_calls"] = []
      if not cont:
        del res["content"]
        
      for tc in self.tool_calls:
        res["tool_calls"].append(dict(
          id=tc["id"],
          type=tc["type"],
          function=dict(
            name = tc["function"]["name"],
            arguments = tc["function"]["arguments"]
          )
        ))
        
    return res
    
  @classmethod
  def from_dict(cls, data: dict):
    """JSON to :class:`shapesinc.Message`"""
    return cls(
      [MessageContent.from_dict(c) for c in data["content"]] if isinstance(data["content"], list) else [MessageContent(data["content"])],
      data["role"],
      tool_calls=data.get("tool_calls", [])
    )
    
  @classmethod
  def new(cls, text: str = "", files: dict = {}, role: str = "user"):
    """Simple method to create a new message
    
    Parameters
    -----------
    text: Optional[:class:`~str`]
      The text which is to be sent.
    files: Optional[:class:`~dict`]
      Files which are to be sent.
    role: Optional[:class:`~str`]
      Role of the sender. Default 'user'
      
    Raises
    -------
    ValueError
      Raised when neither text nor files are given.
    """
    assert text or files, ValueError("Cannot create empty message!")
    c = []
    if text:
      c.append(MessageContent(text))
    if files:
      c.extend([MessageContent (f["url"], f["type"]) for f in files])
      
    return cls(c, role)
    
# Okay, Okay. I know. my naming sense is not too good.

def _p(v):
  if isinstance(v, TypedDict):
    return v
  if isinstance(v, dict):
    return TypedDict(**v)
  if isinstance(v, list):
    return [_p(i) for i in v]
  if isinstance(v, tuple):
    return tuple(_p(i) for i in v)
  if isinstance(v, set):
    return {_p(i) for i in v}

  return v

class TypedDict(dict):
  _default = {}
  _required = []
  
  def __init__(self, **kwargs):
    for i in self._required:
      if i not in kwargs.keys():
        raise ValueError(f"'{i}' is a required argument!")
        
    for k, v in self._default.items():
      if k not in kwargs:
        kwargs[k] = v
    for k, v in kwargs.items():
      v = getattr(self, "_parse_"+k,_p)(v)
      setattr(self, k, v)
      
    super().__init__(**kwargs)

class PromptResponse_Choice(TypedDict):
  """Choice (generated by shape)
  
  Attributes
  -----------
  index: :class:`~int`
    index of the choice
  message: :class:`shapesinc.Message`
    Message
  """
  index: int
  message: Message
  finish_reason: typing.Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
  
  _parse_message = Message.from_dict

class PromptResponse_Usage(TypedDict):
  prompt_tokens: int
  total_tokens: int
  completion_tokens_details: typing.Optional[dict] = None
  prompt_tokens_details: typing.Optional[dict] = None

class PromptResponse(TypedDict):
  """Response generated by Shape
  
  Attributes
  -----------
  id: :class:`~str`
    ID of the request
  model: :class:`~str`
    name of model (shape)
  created: :class:`~datetime.datetime`
    Time when the response was generated
  choices: typing.List[:class:`shapesinc.abc.PromptResponse_Choice`]
    list of choices generated by shape.
  shape: Union[:class:`shapesinc.Shape`, :class:`shapesinc.AsyncShape`]
    Shape which genrated the response.
  """
  id: str
  model: str
  object: typing.Literal["chat.completion"]
  usage: typing.Optional[PromptResponse_Usage] = None
  created: datetime
  choices: typing.List[PromptResponse_Choice]
  
  if typing.TYPE_CHECKING:
    shape: ShapeBase
  
  _parse_created = datetime.fromtimestamp
  _parse_choices = lambda _, cs: [PromptResponse_Choice(**c) for c in cs]
  _parse_usage = lambda _, u: PromptResponse_Usage(**u)

class ToolChoice(str, Enum):
  """Enumeration class for tool choice for specific prompts.

  Attributes
  -----------
  auto:
    {shape} will automatically detect when to use tools.
  none:
    {shape} will not use any tools.
  required:
    {shape} must use tools.
  """
  auto = "auto"
  none = "none"
  required = "required"

Types = typing.Literal[
  "string",
  "number",
  "boolean",
  "integer",
  "object",
  "array",
  "enum",
  "anyOf",
]
class Parameter(TypedDict):
  """Base class for parameters in tool function.
  
  Parameters
  -----------
  description: Optional[:class:`~str`]
    Description of the parameter. This field is optional.
  """
  type: typing.Union[
    Types,
    typing.List[
      typing.Union[
        Types,
        typing.Literal["null"]
      ]
    ]
  ]
  
  def to_dict(self) -> dict:
    """Converts itself into JSON format"""
    d = {}
    for k, v in self.items():
      if isinstance(v, Parameter):
        v=v.to_dict()
      d[k]=v
    if getattr(self, "type", None):
      d["type"] = self.type
      
    return d
    
  def __get__(self): return self.to_dict()

class DictParameter(Parameter):
  _default = {
    "additionalProperties": False
  }
  type = "object"
  properties: typing.Dict[str, Parameter]
  additionalProperties: dict = False
  required: typing.List[str]
  

class StrParameter(Parameter):
  type = "string"
  pattern: str # FT
  format: typing.Literal[
    "date-time",
    "time",
    "date",
    "duration",
    "email",
    "hostname",
    "ipv4",
    "ipv6",
    "uuid"
  ] # FT
  enum: typing.List[str]
  
class NumberParameter(Parameter):
  type = "number"
  multipleOf: typing.Union[float, int] # FT
  maximum: typing.Union[float, int] # FT
  exclusiveMaximum: typing.Union[float, int]
  minimum: typing.Union[float, int] # FT
  exclusiveMinimum: typing.Union[float, int]
  enum: typing.List[typing.Union[float, int]]

class IntParameter(Parameter):
  type = "integer"
  multipleOf: int # FT
  maximum: int # FT
  exclusiveMaximum: int
  minimum: int # FT
  exclusiveMinimum: int
  enum: typing.List[int]

class ListParameter(Parameter):
  type = "array"
  minItems: int # FT
  maxItems: int # FT

class BooleanParameter(Parameter):
  type = "boolean"

class AnyOfParameter(Parameter):
  anyOf: typing.List[Parameter]
  _required=["anyOf"]
  
  def to_dict(self):
    d=super().to_dict()
    res={**d}
    res["anyOf"]=[]
    for v in d["anyOf"]:
      if isinstance(v, Parameter):
        v=v.to_dict()
      res["anyOf"].append(v)
      
    return res

class Function(TypedDict):
  _required = ["name", "description", "parameters"]
  name: str
  description: str
  parameters: DictParameter
  strict: bool = True
  
  def to_dict(self):
    return dict(
      name=self.name,
      description=self.description,
      strict=self.strict,
      parameters=self.parameters.to_dict()
    )
    

class Tool:
  def __init__(
    self,
    function: Function,
    callback
  ):
    self.type = "function"
    self.function = function
    self.callback = callback
    
  def to_dict(self):
    return dict(type=self.type, function=self.function.to_dict())
    
  @classmethod
  def from_function(cls, func) -> "Tool":
    valid_types_map = {
      float: NumberParameter,
      str: StrParameter,
      int: IntParameter,
      bool: BooleanParameter 
    }
    valid_types = tuple(valid_types_map.keys())
    spec = inspect.getfullargspec(func)
    ann = spec.annotations
    params = {}
    for k, v in ann.items():
      assert v in valid_types, TypeError(f"Parameter types of the function must be one of {valid_types}, not {v}")
      params[k]=valid_types_map[v]()
      
    return cls(
      Function(
        name=func.__name__,
        description=func.__doc__ or '',
        parameters=DictParameter(
          required=list(params.keys()),
          **params
        )
      ),
      callback=func
    )

  def call(
    self,
    id: str,
    arguments: str
  ) -> dict:
    args = json.loads(arguments)
    if not inspect.iscoroutinefunction(self.callback):
      res = self.callback(**args)
      return dict(
        role='tool',
        content=str(res),
        tool_call_id = id
      )
      
    async def wrap():
      res = await self.callback(**args)
      return dict(
        role='tool',
        content=str(res),
        tool_call_id = id
      )
      
    return wrap()
