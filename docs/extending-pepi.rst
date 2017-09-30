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

We do not mandate that a ``CameraServer`` must take ``Camera`` objects, but it is **strongly** recommended unless you have a valid reason (e.g. very complicated hardware requirements). The provided Python implementations shows how this may be implemented.

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

Therefore, any of the above languages can be used to implement PEPI server-side components.

Writing New Servers
===================

Interface Definition File
-------------------------

At the heart of PEPI is its interface definition file ``pepi.thrift``. This defines the interface used to access servers and therefore specifies what functions you need to implement.

.. literalinclude:: ../server/pepi.thrift
   :language: c

Depending on the language you choose to implement your new server/camera, the exact format of how you implement these functions will vary, but generally you'll just write the functions exactly as listed (but in the syntax of your language).

From the perspective of writing a server implementation, there are no special requirements from Thrift; you don't need to return Thrift types or use Thrift objects. Your server won't even know its been called from Thrift (sometimes it won't be). Instead, treat component implementations as `handlers` that are called when in response to a Thrift requests, with Thrift managing all the necessary type conversions and network transports.

Python's BaseCameraServer
-------------------------

PEPI provides a minimal implementation of a CameraServer under the class :py:class:`~server.base_camera_server.BaseCameraServer`.

In most cases, :py:class:`~server.base_camera_server.BaseCameraServer` can be used without modification as long as you can provide the ``Camera`` you'd like to use. However, you may wish to override some methods to better suit your use case. For example, :py:class:`~raspi_server.raspi_server.RaspPiCameraServer` overrides the ``identifier()`` method to use the Raspberry Pi's CPU serial number as the ID.

If your server is being implemented in another language, it is still beneficial to refer to this implementation to understand how certain operations are accomplished.

.. literalinclude:: ../server/base_camera_server.py
   :pyobject: BaseCameraServer
   :language: python

Writing New Cameras
===================

If you choose to use a ``Camera`` object with your server, then you should implement your camera according to the ``Camera`` interface.

In Python, :py:class:`~server.abstract_camera.AbstractCamera` is provided as an abstract class with some implemented methods. It is an abstract class rather than a base class (like ``CameraServers``) because it's impossible to cater for all possible connected hardware.

The most important (and tricky) method in a ``Camera`` is it's ``still()`` method that returns a multi-dimensional array of 0-255 RGB pixels (row, column, RGB). For example, ``MyConcreteCamera`` is implemented in Python and captures RGB images at a 4-by-3 pixel resolution:

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

Most physical cameras don't provide a RGB array. The easiest way to transform from JPG or PNG (preferred) files is to use a library such as `Pillow`_ (previously, PIL). In Python, we provide a utility class :py:class:`server.abstract_camera.RGBImage` based on Pillow that can do some of these conversions for you.

.. _Pillow: https://pillow.readthedocs.io/en/3.1.x/index.html

.. code-block:: python
   :emphasize-lines: 1,9,10

   from server import RGBImage
   import numpy as np

   class MyConcreteCamera(AbstractCamera):
      def __init__(self):
         self._camera = MyDSLRCamera()

      def still(self):
         png = self._camera.get_png()
         return np.array(RGBImage.fromstring(png))

Alternatively, if you wish to use Pillow directly:

.. code-block:: python
   :emphasize-lines: 11,12,13,14,15

   from io import BytesIO

   from PIL import Image
   import numpy as np

   class MyConcreteCamera(AbstractCamera):
      def __init__(self):
         self._camera = MyDSLRCamera()

      def still(self):
         png_buffer = BytesIO()
         png_buffer.write(self._camera.get_png())
         png_buffer.seek(0)
         image = Image.open(png_buffer)
         return np.array(Image.open(png_buffer))

Testing Your Camera Implementation
----------------------------------

PEPI includes tests that you can run against your new camera implementation to see if it returns the correct values both natively in Python and over Apache Thrift. Note that this isn't an exhaustive test of your camera implementation and how it handles errors etc., but instead just a test to check the correct values are returned.

To setup these tests against your server, you'll need to define a few `pytest fixtures`_ that is used to "inject" your camera into the tests:

.. code-block:: python
   :emphasize-lines: 7,8,9

   import pytest

   from server.tests import AbstractCameraContract, AbstractCameraOverThrift
   import MyConcreteCamera

   class TestMyConcreteCamera(AbstractCameraContract):
      @pytest.fixture(scope="module")
      def camera(self):
         return MyConcreteCamera()

   class TestDummyCameraOverThrift(AbstractCameraOverThrift):
    @pytest.fixture(scope="module")
    def local_camera(self):
        return MyConcreteCamera()


Refer to the :ref:`Testing` section for more details on testing in PEPI.

.. _pytest fixtures: https://docs.pytest.org/en/latest/fixture.html


Raspi Server Implementation
===========================

A subclass of :py:class:`~server.base_camera_server.BaseCameraServer` is provided with PEPI for use with Raspberry Pi's, :py:class:`~raspi_server.raspi_server.RaspPiCameraServer`. This serves as a useful example on how to extend a language's base implementation to customize functionality.

.. literalinclude:: ../raspi_server/raspi_server.py
   :pyobject: RaspPiCameraServer
   :language: python

As we have previously discussed, in most cases the procedures implemented in :py:class:`~server.base_camera_server.BaseCameraServer` can be used for new servers. Simply subclass :py:class:`~server.base_camera_server.BaseCameraServer` and your new server will inherit all of these implementations, which have been thoroughly tested and refined.

:py:class:`~raspi_server.raspi_server.RaspPiCameraServer` does exactly this: subclasses :py:class:`~server.base_camera_server.BaseCameraServer` and overrides the ``identify()`` procedure to better suit its use case by using the CPU serial number to identify the server (to allow rapid deployment without manual setup on each server). This demonstrates just how easy extendnig servers are (at least in Python, but generally you'll only need one base server to extend written for each language).