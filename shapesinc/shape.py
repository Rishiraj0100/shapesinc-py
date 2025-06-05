import typing

from .abc import (
  ShapeUser as User,
  ShapeChannel as Channel,
  Message,
  PromptResponse,
  MISSING,
  TypedDict
)
from .http import (
  Route,
  AsyncRoute,
  APIError,
  RateLimitError
)


class ShapeBase:
  """Base class for creating shapes.
  
  Parameters
  ------------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape
  app_id: Optional[:class:`~str`]
    Application ID of the shape.
  """
  def __init__(self, api_key: str, username: str, app_id: str = MISSING):
    self.api_key = api_key
    self.username = username
    self.app_id = app_id
    
  @property
  def auth_url(self) -> str:
    """Authorization URL of the shape"""
    if self.app_id is MISSING:
      raise ValueError("app_id was not found for the given shape.")
      
    return Route.SITE/"authorize?app_id="+self.app_id

  @property
  def type(self) -> typing.Literal["SYNCHRONOUS", "ASYNCHRONOUS"]:
    """Tells whether the instance is configured for asynchronous environment or synchronous"""
    raise NotImplementedError

  @property
  def api_key(self) -> str:
    """API key"""
    return self.__api_key

  @api_key.setter
  def api_key(self, value: str):
    self.__api_key = value

  @property
  def model_name(self) -> str:
    """Name of model of your shape"""
    return "shapesinc/"+self.username
    
  def prompt(
    self,
    message: Message,
    user: User = None,
    channel: Channel = None,
    remove_uid: bool = False
  ) -> typing.Union[PromptResponse, typing.Awaitable[PromptResponse]]:
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }
    if self.app_id is not MISSING:
      headers["X-App-ID"] = self.app_id
    if user is not None:
      headers["X-User-Id"] = user.id
      if user.auth_token and self.app_id is not MISSING:
        headers["X-User-Auth"] = user.auth_token
        if remove_uid:
          del headers["X-User-Id"]
        del headers["Authorization"]
        
    if channel is not None:
      headers["X-Channel-Id"] = channel.id
      
    if isinstance(message, str):
      message=Message.new(message)
      
    return self.make_send_message_request([message.to_dict()], headers)

  def make_send_message_request(
    self,
    messages: typing.List[typing.Dict[str, str]],
    headers: typing.Dict[str, str]
  ) -> PromptResponse:
    """The method which is implemented to make requests to API

    Raises
    -------
    NotImplementedError
    """
    raise NotImplementedError

class Shape(ShapeBase):
  """Creates a shape for synchronous environment.
  
  It is a subclass of :class:`shapesinc.ShapeBase`

  Parameters
  ------------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape
  app_id: Optional[:class:`~str`]
    Application ID of the shape.

  Example
  ---------
  
  .. code-block:: python3
    
      import shapesinc
      shape = shapesinc.Shape("API_KEY", "Myshape")
      
      def run():
        while True:
          q = input(" >>> ")
          print(shape.prompt(q))

  """
  type: str = "SYNCHRONOUS"
  
  def prompt(self, *args, **kwargs) -> PromptResponse:
    """Send a prompt through the shape
    
    Parameters
    -----------
    message: Union[:class:`shapesinc.Message`, :class:`~str`]
      The message which is to be sent to the shape. Can be a :class:`shapesinc.Message` or a string.
    user: Optional[:class:`shapesinc.ShapeUser`]
      The user who is sending the message.
    channel: Optional[:class:`shapesinc.ShapeChannel`]
      The channel in which the message is being sent. Used for context.
      
    Returns
    --------
    :class:`shapesinc.PromptResponse`
      The response of the prompt.
      
    Raises
    -------
    :class:`shapesinc.RateLimitError`
      Error when we get ratelimited
    :class:`shapesinc.APIError`
      Error raised by shapes.inc API.
    """
    return super().prompt(*args, **kwargs)

  def make_send_message_request(
    self,
    messages: typing.List[typing.Dict[str, str]],
    headers: typing.Dict[str, str]
  ) -> PromptResponse:
    return PromptResponse(shape=self, **(Route.API_BASE/"chat/completions").request(
      "POST",
      headers,
      {
        "model": self.model_name,
        "messages": messages
      }
    ))
    
  def info(self) -> dict:
    """Tells information about shape.
    
    Returns
    --------
    :class:`~dict`
      Reponse from API
    """
    res = (Route/"shapes/public"/self.username).request("GET")
    return TypedDict(**res)


class AsyncShape(ShapeBase):
  """Creates a shape for synchronous environment.
  
  It is a subclass of :class:`shapesinc.ShapeBase`

  Parameters
  ------------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape
  app_id: Optional[:class:`~str`]
    Application ID of the shape.

  Example
  ---------
  
  .. code-block:: python3
    
      import shapesinc
      shape = shapesinc.AsyncShape("API_KEY", "Myshape")
      
      async def run():
        while True:
          q = input(" >>> ")
          print(await shape.prompt(q))

  """
  type: str = "ASYNCHRONOUS"
  
  async def prompt(self, *args, **kwargs) -> PromptResponse:
    """Send a prompt through the shape
    
    Parameters
    -----------
    message: Union[:class:`shapesinc.Message`, :class:`~str`]
      The message which is to be sent to the shape. Can be a :class:`shapesinc.Message` or a string.
    user: Optional[:class:`shapesinc.ShapeUser`]
      The user who is sending the message.
    channel: Optional[:class:`shapesinc.ShapeChannel`]
      The channel in which the message is being sent. Used for context.
      
    Returns
    --------
    :class:`shapesinc.PromptResponse`
      The response of the prompt.
    Raises
    -------
    :class:`shapesinc.RateLimitError`
      Error when we get ratelimited
    :class:`shapesinc.APIError`
      Error raised by shapes.inc API.
    """
    return await super().prompt(*args, **kwargs)

  async def make_send_message_request(
    self,
    messages: typing.List[typing.Dict[str, str]],
    headers: typing.Dict[str, str]
  ) -> PromptResponse:
    req = await (AsyncRoute.API_BASE/"chat/completions").request(
      "POST",
      headers,
      {
        "model": self.model_name,
        "messages": messages
      }
    )
    return PromptResponse(shape=self, **req)
    
  async def info(self) -> dict:
    """Tells information about shape.
    
    Returns
    --------
    :class:`~dict`
      Reponse from API
    """
    res = await (AsyncRoute/"shapes/public"/self.username).request("GET")
    return TypedDict(**res)


def shape(
  api_key: str,
  username: str,
  app_id: str = MISSING,
  *,
  synchronous: bool = True
) -> typing.Union[Shape, AsyncShape]:
  """Creates a new instance for a shape if none exists; otherwise, returns the original instance.

  Parameters
  -----------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape
  app_id: Optional[:class:`~str`]
    Application ID of the shape.
  synchronous: Optional[:class:`~bool`]
    Whether the instance is to be configured for synchronous environment or asynchronous. Default: True
  
  Returns
  --------
  :class:`shapesinc.Shape`
    If the value of synchronous is set to True.
  :class:`shapesinc.AsyncShape`
    If the value of synchronous is set to False.
  """
  return (Shape if synchronous else AsyncShape)(api_key, username, app_id)
