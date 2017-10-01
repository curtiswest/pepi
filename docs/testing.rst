.. _testing:

=======
Testing
=======

Components need to adhere properly to their respective interface definition to maintain compatibility in the system. To check this, we provide test cases implemented in Python (based on the Pytest framework).

Given Python's duck-typing mechanism, it can natively test implemetations in any language, so we only need one test definition. To 'inject' your component, no matter the language, you simply need to subclass and provide an instance of your to-be-tested object.

Running Tests
=============

Setting up to run the test cases requires a few steps:

#. CD into the PEPI base directory: ``cd pepi``
#. Install the test's Python package requirements: ``pip install -r test/requirements.txt``

And then running the tests simply requires a single command: ``PYTHONPATH=$PWD:$PYTHONPATH py.test``

Testing Camera Components
=========================

Python Cameras
--------------

Python native components are the simplest to test. We provide tests for both local Python object components, and Python components being served over Thrift. In both cases, you just need to provide an instance of your component class in the below test fixtures and the rest will be handled.

.. code-block:: python
   :emphasize-lines: 9,14

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

Non-Python Cameras
------------------

It is still possible to test non-Python components with the provided Python test classes, but you'll need to launch the component's Thrift server yourself (perhaps with some script, depending on your language).

Suppose your server is accessible at *192.168.1.10:6000*, then we can utilise duck-typing to convince the Python local object test cases that they are just working with a local object. This achieved as follows:

.. code-block:: python
   :emphasize-lines: 10,11

   import pytest

   from server import pepi_thrift
   from server.tests import AbstractCameraContract, AbstractCameraOverThrift
   from thriftpy.rpc import client_context

   class TestMyNonPythonConcreteCamera(AbstractCameraContract):
      @pytest.fixture(scope="module")
      def camera(self):
         with client_context(pepi_thrift.Camera, '192.168.1.10', 6000) as c:
            return c

Testing Servers
===============

Testing servers is much the same as testing cameras -- just targeting different test fixtures.

Python Servers
--------------

.. code-block:: python
   :emphasize-lines: 12,17

   import pytest

   from server import pepi_thrift
   from server.tests import MetaCameraServerContract
   from thriftpy.rpc import client_context

   import MyPythonServer

   class TestMyNonPythonServer(MetaCameraServerContract):
      @pytest.fixture(scope="module")
      def server(self):
         return MyPythonServer()

   class TestMyPythonServerOverThrift(MetaCameraServerContractOverThrift):
      @pytest.fixture(scope="module")
      def local_server(self):
         return MyPythonServer()


Non-Python Servers
------------------

Again, non-Python servers can still be tested, but you'll need to launch the launch the component's Thrift server yourself. Suppose your sever is accessible at *192.168.1.10:6000*:

.. code-block:: python
   :emphasize-lines: 10,11

   import pytest

   from server import pepi_thrift
   from server.tests import MetaCameraServerContract
   from thriftpy.rpc import client_context

   class TestMyNonPythonServer(MetaCameraServerContract):
      @pytest.fixture(scope="module")
      def server(self):
         with client_context(pepi_thrift.CameraServer, '192.168.1.10', 6000) as c:
            return c
