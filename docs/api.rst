.. currentmodule:: shapesinc

API Reference
=============

The following section outlines the API of shapesinc module

Shapes
-------

Bases
~~~~~~
.. autoclass:: shapesinc.ShapeBase
    :members:

.. autofunction:: shapesinc.shape

Shape
~~~~~~

.. attributetable:: shapesinc.Shape

.. autoclass:: shapesinc.Shape
    :members:


AsyncShape
~~~~~~~~~~~

.. attributetable:: shapesinc.AsyncShape

.. autoclass:: shapesinc.AsyncShape
    :members:

ABC
----

Bases
~~~~~~

.. autoclass:: shapesinc.abc.ABCBase
    :members:

.. autoclass:: shapesinc.ShapeUser
    :members:
      
.. autoclass:: shapesinc.ShapeChannel
    :members:

Message
~~~~~~~~

.. attributetable:: shapesinc.MessageContent

.. autoclass:: shapesinc.MessageContent
    :members:

.. attributetable:: shapesinc.Message

.. autoclass:: shapesinc.Message
    :members:

.. autoclass:: shapesinc.ContentType

.. autoclass:: shapesinc.PromptResponse

.. autoclass:: shapesinc.abc.PromptResponse_Choice

Tools
~~~~~~

.. autoclass:: shapesinc.Parameter
    :members:

.. autoclass:: shapesinc.StrParameter

.. autoclass:: shapesinc.IntParameter

.. autoclass:: shapesinc.NumberParameter

.. autoclass:: shapesinc.BooleanParameter

.. autoclass:: shapesinc.ListParameter

.. autoclass:: shapesinc.DictParameter

.. autoclass:: shapesinc.AnyOfParameter

.. autoclass:: shapesinc.Function
    :members:

.. autoclass:: shapesinc.Tool
    :members:

.. autoclass:: shapesinc.ToolChoice

HTTP
-----

Routes
~~~~~~~

.. autoclass:: shapesinc.http._RouteBase
    :members:

.. autoclass:: shapesinc.http._Route
    :members:

.. autoclass:: shapesinc.http._AsyncRoute
    :members:

Errors
~~~~~~~

.. autoclass:: shapesinc.APIError

.. autoclass:: shapesinc.RateLimitError
