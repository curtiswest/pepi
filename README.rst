====
PEPI
====

    "A Portable, Extensible Photogrammetry Instrument."

.. image:: https://travis-ci.org/curtiswest/pepi.svg?branch=master
   :target: https://travis-ci.org/curtiswest/pepi
   :alt: Build/Test Status
.. image:: https://readthedocs.org/projects/pepi/badge/?version=latest
   :target: http://pepi.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://landscape.io/github/curtiswest/pepi/master/landscape.svg?style=flat
   :target: https://landscape.io/github/curtiswest/pepi/master
   :alt: Code Health
.. image:: https://codecov.io/gh/curtiswest/pepi/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/curtiswest/pepi
   :alt: Code Coverage

PEPI is a software platform that enables remote command and control of servers with connected cameras. PEPI is used for the purposes of acquiring stereo-photogrammetry imagery. It seamlessly supports any number of connected servers without any required manual setup.

PEPI is designed to be expanded upon. The implementation in this repo is purely Python-based for a Raspberry Pi with Camera Module, but it is built upon Apache Thrift. Therefore, any correct implementation in an Apache Thrift supported language should work out of the box. This means that as long as you can write a camera 'adapter' that adheres to the PEPI standard, you can use it with PEPI.

Links
=====
* PEPI is licensed under `Apache-2.0 <https://github.com/curtiswest/pepi/blob/master/LICENSE>`_.
* PEPI's source code is `available on GitHub <https://github.com/curtiswest/pepi>`_.
* PEPI's documentation is `available on ReadTheDocs <https://pepi.readthedocs.io/en/latest/>`_.
* PEPI uses a continuous integration system provided by Travis CI; `view the test results on Travis-CI <https://travis-ci.org/curtiswest/pepi>`_.

Built With
==========
* `Python 2 & 3 <https://www.python.org/>`_ - This implementation is built on Python 2.7 and should be compatible with Python 3.6. Python is not strictly required for software on either end, should the use of another language be desirable.
* `Apache Thrift <https://thrift.apache.org/>`_ - A software framework for scalable, cross-language services
* `Picamera <https://picamera.readthedocs.io/>`_ - A pure Python interface to the Raspberry Pi Camera Module
* `Flask <http://flask.pocoo.org/>`_ - A web microframework for Python, used for the included user interface
* ..and many more packages gracefully provided by the Python community.

Authors & Acknowledgements
==========================

* `Claudio Pizzolato <https://github.com/cpizzolato>`_ - *Initial work and proof of concept*
* `Curtis West <https://github.com/curtiswest>`_- *Development from proof of concept through to version 2.0*
* Griffith University - *For supporting the project*
