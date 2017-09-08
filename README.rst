====
PEPI
====
.. image:: https://travis-ci.org/curtiswest/pepi.svg?branch=master
   :target: https://travis-ci.org/curtiswest/pepi
   :alt: Build/Test Status
.. image:: https://readthedocs.org/projects/pepi/badge/?version=latest
   :target: http://pepi.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://api.codacy.com/project/badge/Grade/6873aa2fa807419a8d3321e071479919
   :target: https://www.codacy.com/app/curtiswest/pepi?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=curtiswest/pepi&amp;utm_campaign=Badge_Grade
   :alt: Codacy Code Health
.. image:: https://codecov.io/gh/curtiswest/pepi/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/curtiswest/pepi
   :alt: Code Coverage


"A Portable, Extensible Photogrammetry Instrument."

PEPI is a software platform that enables remote command and control of servers with connected cameras. PEPI is used for the purposes of acquiring stereo-photogrammetry imagery. It seamlessly supports any number of connected servers without any required manual setup.

PEPI is designed to be expanded upon. The implementation in this repo is purely Python-based for a `Raspberry Pi`_ with Camera Module, but it is built upon `Apache Thrift`_. Therefore, any correct implementation in an Apache Thrift supported language should work out of the box. This means that as long as you can write a camera 'adapter' that adheres to the PEPI standard, you can use it with PEPI.

Links
=====
* PEPI is licensed under the `Apache-2.0 license`_.
* PEPI's `source code`_ is available on GitHub.
* PEPI's `documentation`_ is available on ReadTheDocs.
* PEPI uses a continuous integration and testing system provided by `Travis CI`_.

Built With
==========
* `Python 2 & 3 <https://www.python.org/>`_ - This implementation is built on Python 2.7 and should be compatible with Python 3.6. Python is not strictly, should the use of another language be desirable.
* `Apache Thrift`_ - A software framework for scalable, cross-language services
* `PiCamera`_ - A pure Python interface to the Raspberry Pi Camera Module
* `Flask <http://flask.pocoo.org/>`_ - A web microframework for Python, used for the included user interface
* ..and many more packages gracefully provided by the Python community.

Authors & Acknowledgements
==========================

* `Claudio Pizzolato <https://github.com/cpizzolato>`_ - *Initial work and proof of concept*
* `Curtis West <https://github.com/curtiswest>`_- *Development from proof of concept through to version 2.0*
* Griffith University - *For supporting the project*


.. _Raspberry Pi: https://www.raspberrypi.org/
.. _camera: https://www.raspberrypi.org/learning/getting-started-with-picamera/
.. _PiCamera: https://www.raspberrypi.org/learning/getting-started-with-picamera/
.. _documentation: https://pepi.readthedocs.io/
.. _source code: https://github.com/curtiswest/pepi/
.. _Travis CI: https://travis-ci.org/curtiswest/pepi/
.. _Apache-2.0 license: https://github.com/curtiswest/pepi/blob/master/LICENSE/
.. _Apache Thrift: https://thrift.apache.org/
