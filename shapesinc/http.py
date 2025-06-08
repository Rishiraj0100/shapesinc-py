import aiohttp
import json
import sys
import typing
import urllib.request as request

from urllib.error import HTTPError

from .__info__ import __version__


vi = sys.version_info
PYTHON_VERSION = f"{vi.major}.{vi.minor}.{vi.micro}{vi.releaselevel}{vi.serial}".split("final")[0]


class _RouteBase(str):
  """BaseClass for HTTP activities.
  It is a subclass of :class:`~str`
  """
  def __call__(self, v):
    return self.__class__(v)

  @property
  def BASE(self) -> str:
    """Base url of API"""
    return self.__class__("https://api.shapes.inc")
  
  @property
  def SITE(self) -> str:
    """URL of site"""
    return self.__class__("https://shapes.inc")

  @property
  def API_BASE(self) -> str:
    """URL for AI API interaction"""
    return self.BASE/"v1"

  def __truediv__(self, o: str):
    val = self.rstrip("/")
    return self.__class__(val+"/"+o)

  def request(
    self,
    method: str = "POST",
    headers: dict = {},
    data: dict = {},
    is_json: bool = True
  ):
    """This method is implemented to make requests
    
    Parameters
    -----------
    method: Optional[:class:`~str`]
      method of the operation. Default: "POST"
    headers: Optional[:class:`~dict`]
      Headers for the request
    data: Optional[:class:`~dict`]
      Data to post.
    is_json: Optional[:class:`~bool`]
      whether the response will be in JSON format or not. default: True

    Raises
    -------
    NotImplementedError
    """
    raise NotImplementedError

class _Route(_RouteBase):
  """Used for synchronous purpose.
  It is a subclass of :class:`shapesinc.http._RouteBase`"""
  def request(
    self,
    method: str = "POST",
    headers: dict = {},
    data: dict = {},
    is_json: bool = True
  ) -> typing.Union[bytes, dict]:
    """This method is implemented to make requests.
    
    Parameters
    -----------
    method: Optional[:class:`~str`]
      method of the operation. Default: "POST"
    headers: Optional[:class:`~dict`]
      Headers for the request
    data: Optional[:class:`~dict`]
      Data to post.
    is_json: Optional[:class:`~bool`]
      whether the response will be in JSON format or not. default: True
      
    Returns
    --------
    :class:`~bytes`
      If the data is not in JSON format.
    :class:`~dict`
      If the data is in JSON format.
      
    Raises
    -------
    :class:`shapesinc.RateLimitError`
      We are being ratelimited.
    :class:`shapesinc.APIError`
      Other errors
    """
    method = method.upper()
    if method != "GET" and isinstance(data, dict):
      headers["Content-Type"] = "application/json"

    headers["User-Agent"] = f"Shapes.inc API Wrapper Py using Python/{PYTHON_VERSION} shapesinc-py/{__version__}"
    
    kw={}
    if method!="GET":
      kw["data"] = json.dumps(data).encode()

    req = request.Request(
      self,
      headers = headers,
      **kw
    )
    try:
      req = request.urlopen(req)
    except HTTPError as req:
      try:
        res = json.loads(req.read())
      except: res = req.read()
      
      e = RateLimitError if req.code == 429 else APIError
      raise e(res, req.code)

    res = json.loads(req.read()) if is_json else req.read()
    return res

class _AsyncRoute(_RouteBase):
  """Used for asynchronous purpose.
  It is a subclass of :class:`shapesinc.http._RouteBase`"""
  async def request(
    self,
    method: str = "POST",
    headers: dict = {},
    data: dict = {},
    is_json: bool = True
  ) -> typing.Union[bytes, dict]:
    """This method is implemented to make requests.
    
    Parameters
    -----------
    method: Optional[:class:`~str`]
      method of the operation. Default: "POST"
    headers: Optional[:class:`~dict`]
      Headers for the request
    data: Optional[:class:`~dict`]
      Data to post.
    is_json: Optional[:class:`~bool`]
      whether the response will be in JSON format or not. default: True
      
    Returns
    --------
    :class:`~bytes`
      If the data is not in JSON format.
    :class:`~dict`
      If the data is in JSON format.
      
    Raises
    -------
    :class:`shapesinc.RateLimitError`
      We are being ratelimited.
    :class:`shapesinc.APIError`
      Other errors
    """
    method = method.upper()
    kw = {}
    if method!="GET":
      kw["json"] = data

    async with aiohttp.ClientSession() as ses:
      data = await ses.request(
        method,
        self,
        headers = headers,
        **kw
      )
      sc = data.status
      res = await (data.json() if is_json else data.text())
      
    if sc==200:
      return res
      
    if sc == 429:
      raise RateLimitError(res, sc)
      
    raise APIError(res, sc)
    

RouteBase=_RouteBase().BASE
Route=_Route().BASE
AsyncRoute=_AsyncRoute().BASE

class APIError(Exception):
  """Base class for API exceptions"""
  def __init__(self, data: dict, code: int):
    if isinstance(data, str):
      data={"error":{"message":data}}
    self.message = data["error"]["message"]
    self.data = data
    self.code = code
    super().__init__(f"[{code}]: "+data["error"]["message"])
    
class RateLimitError(APIError):
  """Raised when API is being ratelimited"""
