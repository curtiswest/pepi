.. _extending-pepi:

==============
Extending PEPI
==============

Generally, you'll want to extend PEPI by creating new servers and adding support for new cameras. The client-side software should work with any server out-of-the-box, but there are still some features that need to be added to the client.

PEPI Theory
===========

PEPI can be divided into the client-side and the server-side. As discussed, the client-side doesn't really need to be extended--the server is where the interesting extensions can happen.

Servers can be divided into two components:

* The actual server itself (the ``CameraServer``)
* Cameras connected to the server (the ``Camera``)

Depending on how you implement you server, you make choose to make these one and the same (i.e. hardcoded camera), or have the server accept any valid camera. The provided `Raspi Server Implementation`_ does the latter and defines a generic way to approach this problem in Python.

Languages
---------

PEPI is indifferent to which language you implement your server in, so long as it can be accessed over Apache Thrift. Thrift's language bindings include:

* C++
* C#
* Cocoa
* D
* Delphi
* Erlang
* Haskell
* Java
* OCaml
* Perl
* PHP
* Python
* Ruby
* Smalltalk
* ..plus others in the works or supported by third parties

Therefore, any of the above languages can be used to implement a PEPI server.

Interface Definition File
-------------------------

At the heart of PEPI is its interface definition file ``pepi.thrift``. This defines the interface used to access servers and therefore specifies what functions you need to implement.

.. literalinclude:: ../server/pepi.thrift
   :linenos:
   :language: c


Raspi Server Implementation
===========================

Coming soon..
