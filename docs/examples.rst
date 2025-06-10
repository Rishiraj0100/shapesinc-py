Examples
==========

Synchronous Shape Example
---------------------------

.. code-block:: python3

    from shapesinc import (
      shape,
      ShapeUser as User,
      ShapeChannel as Channel
    )
    
    my_shape = shape("API_KEY", "my_shape", "app_id")
    user = User("u0")
    channel = Channel("cli")
    
    while True:
      inp = input(" >>> ")
      r = my_shape.prompt(inp, user = user, channel=channel)
      print(r.choices[0].message)
    
Asynchronous Shape Example
----------------------------

.. code-block:: python3

    from shapesinc import (
      shape,
      ShapeUser as User,
      ShapeChannel as Channel
    )
    
    my_shape = shape("API_KEY", "my_shape", "app_id", synchronous=False)
    user = User("u0")
    channel = Channel("cli")
    
    async def run():
      while True:
        inp = input(" >>> ")
        r = await my_shape.prompt(inp, user = user, channel=channel)
        print(r.choices[0].message)
    
    import asyncio
    asyncio.run(run())


Image Message Examples
-----------------------

.. code-block:: python3

    from shapesinc import Message, MessageContent, ContentType as C
    
    msg = Message.new("Explain this image!", [dict(url = "URL OF IMAGE", type = c.image)])
    resp = my_shape.prompt(msg)
    
Audio Messages
---------------

.. code-block:: python3

    from shapesinc import Message, MessageContent, ContentType as C
    
    msg = Message.new(files = [dict(url = "URL OF AUDIO FILE", type = c.audio)])
    resp = my_shape.prompt(msg)


Tools Example
--------------

.. code-block:: python3

    from shapesinc import Tool

    # Synchronous Example
    def add(a: float, b: float):
        '''Adds two numbers'''
        return a + b

    tool1 = Tool.from_function(add)
    my_shape.prompt(
        "can you add 2 and 4 for me using tools please?",
        tools=[tool1],
        user=user,
        channel=channel
    )

    # Asynchronous Example
    async def multiply(a: float, b: float):
        '''Multiplies two numbers'''
        return a * b

    tool2 = Tool.from_function(multiply)

    # NOTE: Tools with Asynchronous functions must not go with Synchronous Shapes.
    await my_shape.prompt(
        "can you multiply 2 and 4 for me using tools please?",
        tools=[tool2],
        user=user,
        channel=channel
    )
