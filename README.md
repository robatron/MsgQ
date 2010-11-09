# MsgQ

MsgQ is short for "Message Queue". It is a simple, web-based utility that allows one to push and pop messages off of a queue. There is also an optional blocking mechanism that allows the server to act "busy" while waiting for a message. This is handy for (almost) instant server-to-client communication.

This is based on the idea of the [messenger component](http://trac.osuosl.org/git/?p=touchscreen.git;a=blob_plain;f=core/messenger.tac;hb=c60491d32feb22ade5aa6abc6bbf925c12c3f427) of the [Touchscreen project](http://trac.osuosl.org/trac/touchscreen).

## Server-side setup

To start MsgQ, just run 

    python msgq-serv.py

### Dependancies

 - Python >= v2.6.5
 - CherryPy >= v3.1.2

If you're on Ubuntu (like me), you should be able to simply run the following command to install them both:

    sudo apt-get install python-cherrypy

## Client-side usage

Here are some example uses for MsgQ on the client side:

### Push

To push a message onto a queue, first specify the `queue`, and set `msg` to your message. In the following example, we're pushing a message "O HAI!!" onto the queue "fooQ":

    http://localhost:8080/push?queue=fooQ&msg=O HAI!!

If the queue does not exist, it will be created. If the message is not set, or some other error occurs, the error will be returned. If everything went well, a '0' will be returned.

### Pop

To pop a message off of a queue, you only need to specify the `queue`. In the following example, we're popping a message of the "fooQ" queue:

    http://localhost:8080/pop?queue=fooQ

The top message on the specified queue will be returned. Trying to pop a message off of a deleted queue will result in a "{{empty queue}}" being returned.

#### Waiting for a message

Optionally, you can make MsgQ wait for a message to be placed on the queue. This will cause MsgQ to look "busy" to the client while it waits. This is handy for (almost) instant server-to-client communication. 

Make MsgQ wait by setting the `wait` parameter to the number of milliseconds the queue should wait before it times out, and reports "{{empty queue}}". In the following example, MsgQ will wait for 5 seconds:

    http://localhost:8080/pop?queue=fooQ&wait=5000

If a message gets placed on the queue while it's waiting, MsgQ will return with it right away. If no message gets placed on the queue before the wait time is up, it will return with an "{{empty queue}}".

Setting `wait` to a negative number will result in it waiting indefinitely.

### Demo

You can view an interactive demo by starting the server and going to `/demo` or the root:

    http://localhost:8080/demo

or

    http://localhost:8080/