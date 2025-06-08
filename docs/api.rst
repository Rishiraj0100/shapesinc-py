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
