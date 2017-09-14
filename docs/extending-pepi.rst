.. _extending-pepi:

==============
Extending PEPI
==============

Generally, you'll want to extend PEPI by creating new servers and adding support for new cameras. The client-side software should work with any server out-of-the-box, but there are still `some features`_ that need to be added to the client.

.. _some features: https://github.com/curtiswest/pepi/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aopen%20label%3Aenhancement%20client

PEPI Theory
===========

PEPI can be divided into the client-side and the server-side. As discussed, the client-side doesn't really need to be extended--the server is where the interesting extensions can happen.

Servers can be divided into two components:

* The actual server itself (the ``CameraServer``)
* Cameras connected to the server (the ``Camera``)

A ``CameraServer`` is not `required` to take ``Camera`` objects, but it is strongly recommended. The provided Python implementations shows how this may be implemented.

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

.. note::
   PEPI is currently limited in mixing languages within a server implementation. There is no provided support as yet for a Python server accessing a C camera, for example.

   There are `suggestions`_ on how to enable cross-language camera to server communication by using Apache Thrift locally, but this design has not been fully explored. Nonetheless, you should refer to the :py:class:`server.abstract_camera.AbstractCamera` class as the definitive implementation of a camera, as compatibility with it will be supported in the future.

   .. _suggestions: https://github.com/curtiswest/pepi/issues/6

Writing New Servers
===================

Interface Definition File
-------------------------

At the heart of PEPI is its interface definition file ``pepi.thrift``. This defines the interface used to access servers and therefore specifies what functions you need to implement.

.. literalinclude:: ../server/pepi.thrift
   :linenos:
   :language: c

Depending on the language you choose to implement your new server/camera, the exact format of how you implement these functions will vary, but generally you'll just write the functions exactly as listed (but in the syntax of your language).

From the perspective of writing a server implementation, there are no special requirements from Thrift; you don't need to return Thrift types or use Thrift objects. Instead, think of the above ``CameraServer`` service as a `handler` that is called when a Thrift requests occurs, with Thrift managing all the necessary type conversions.

Python's BaseCameraServer
-------------------------

PEPI provides a minimal implementation of a CameraServer under the class :py:class:`server.base_camera_server.BaseCameraServer`.

In most cases, ``BaseCameraServer`` can be used without modification. However, you may wish to override some methods to better suit your use case. For example, ``RaspiCameraServer`` overrides the ``identifier()`` method to use the Raspberry Pi's CPU serial number as the ID.

If your server is being implemented in another language, it is still beneficial to refer to this implementation to understand how certain operations are accomplished.

.. literalinclude:: ../server/base_camera_server.py
   :pyobject: BaseCameraServer
   :linenos:
   :language: python

Writing New Cameras
===================

If you choose to use a ``Camera`` object with your server, then you should implement your camera according to the ``AbstractCamera`` interface.

In Python, :py:class:`server.abstract_camera.AbstractCamera` is provided as an abstract class with some implemented methods. You should refer to this class when implementing cameras in other languages too.

The most important method in a ``Camera`` is it's ``still()`` method that returns a multi-dimensional array of 0-255 RGB pixels (row, column, RGB). For example, ``MyConcreteCamera`` is implemented in Python and captures RGB images at a 4-by-3 pixel resolution:

.. code-block:: python

   >>> camera = MyConcreteCamera()
   >>> image = camera.still()
   >>> print(type(image))
   <type 'numpy.ndarray'>
   >>> print(image.shape)
   (3, 4, 3)
   >>> image
       array([[[244, 213,  53],  # Row 1, Col 1
               [141, 130, 195],  #        Col 2
               [229, 156,  94],  #        Col 3
               [204,  19, 191]], #        Col 4

              [[105, 202, 239],  # Row 2, Col 1
               [183, 109, 243],  #        Col 2
               [164, 190,   1],  #        Col 3
               [216, 191,  63]], #        Col 4

              [[160, 232, 240],  # Row 3, Col 1
               [ 86, 186, 252],  #        Col 2
               [ 19, 212, 221],  #        Col 3
               [253, 143,  29]]], dtype=uint8)  # Col 4

Most physical cameras don't provide a RGB array. The easiest way to transform from JPG or PNG (preferred) files is to use a library such as `Pillow`_ (previously, PIL). For example, if your physical camera returns a PNG encoded string when you call ``get_png()``, you can transform this to the proper RGB array as follows:

.. _Pillow: https://pillow.readthedocs.io/en/3.1.x/index.html

.. code-block:: python
   :emphasize-lines: 10,11

   from PIL import Image
   import numpy as np

   class MyConcreteCamera(MetaCamera):
      def __init__(self):
         self._camera = MyDSLRCamera()

      def still(self):
         png = self._camera.get_png()
         image = Image.fromstring(png)
         return np.array(image)

Testing Your Camera Implementation
----------------------------------

PEPI includes tests that you can run against your new camera implementation to see if it returns the correct values. Note that this isn't an exhaustive test of your camera implementation and how it handles errors etc., but instead just a test to check the correct values are returned.

To setup these tests against your server, you'll need to define a `pytest fixture`_ that is used to "inject" your camera into the tests:

.. code-block:: python
   :emphasize-lines: 7,8,9

   import pytest

   from server.tests import MetaCameraContract
   import MyConcreteCamera

   class TestMyConcreteCamera(MetaCameraContract):
      @pytest.fixture(scope="module")
      def camera(self):
         return MyConcreteCamera()

Refer to the :ref:`Testing` section for more details on testing in PEPI.

.. _pytest fixture: https://docs.pytest.org/en/latest/fixture.html


Raspi Server Implementation
===========================

A subclass of ``BaseCameraServer`` is provided with PEPI for use with Raspberry Pi's, ``RaspPiCameraServer``. This serves as a useful example on how to create your own servers based on ``BaseCameraServer``.

.. literalinclude:: ../raspi_server/raspi_server.py
   :pyobject: RaspPiCameraServer
   :linenos:
   :language: python

As we have previously discussed, in most cases the procedures implemented in ``BaseCameraServer`` can be used for new servers. Simply subclass ``BaseCameraServer`` and your new server will inherit all of these implementations, which have been thoroughly tested and refined.

``RaspPiCameraServer`` does exactly this: subclasses ``BaseCameraServer`` and overrides the ``identify()`` procedure to better suit its use case. This demonstrates just how easy writing new servers are (at least in Python, but generally you'll only need one server written for each language).