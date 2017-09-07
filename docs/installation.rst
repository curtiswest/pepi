.. _installation:

============
Installation
============

.. note::
  These installation notes are mainly for the provided PEPI implementations, running on the specified :ref:`hardware`. Configurations outside this scope may require different setup steps.

Prerequisites
=============

Python
------
The included client and servers use Python 2.6/3.6 or greater. Other versions may work, but are untested. You can check this in your terminal:

.. code-block:: console

  $ python --version
  Python 2.7.13
  $ python --version
  Python 3.6.1

If you have an old version, or you get errors about Python not being recognised, you should follow the `Python Install Guide <https://wiki.python.org/moin/BeginnersGuide/Download>`_.

Raspberry Pi
------------
The provided implementations should run on any Raspberry Pi, but has only been tested on a RPi 3. The OS distro that you use shouldn't matter, but we suggest `Raspbian`_ (or Raspbian Lite for maximum performance). You'll need a microSD card - 8GB is perfect.

Unless you plan on plugging a keyboard, mouse and monitor into your Pis, you'll probably be using SSH to control them. It is important to note that, by default, SSH comes **disabled** unless you configure the flash SD card before boot. If you plan on SSH and you're running the Pi's over Wi-fi, you'll need to add your Wi-Fi details to the SD card before boot too.

Enabling SSH
~~~~~~~~~~~~
#. Download the `Raspbian`_ image you wish to use.
#. Flash the Raspbian image to your SD card. You can use a number of tools for this, we recommend `Etcher <https://etcher.io/>`_.
#. After flashing the SD card, eject it then reinsert it. You should see it mounted in your file explorer, usually called ``BOOT``.
#. Open the SD card in your file explorer.
#. Create a new file in the root of the SD CARD called exactly ``ssh``, **without any file extension** to enable SSH by default on this SD card.

Configuring Wi-Fi
~~~~~~~~~~~~~~~~~
#. Open your file exporer to the root of your flashed SD card.
#. Navigate to ``/etc/wpa_supplicant/``.
#. Locate and open the ``wpa_supplicant.conf`` file in your favourite text editor (not Windows Notepad!)
#. Add to the following code block to the bottom of that file (or edit it, if it already exists). Replace SSID and PASSWORD with your intended wireless network's details.

   .. code-block:: text

     network={
      ssid="SSID"
      psk="PASSWORD"
     }

#. Save the file back to the SD card.

Camera Module
-------------
The included server implementation (:py:mod:`raspi_server`) needs a properly installed and configured Raspberry Pi Camera Module.

PiCamera has provided a great `quickstart guide`_ on this process. However, if you are using SSH (ie. a terminal) to connect to your Raspberry Pi, you cannot complete the last steps in that guide as it requires a GUI.

To enable the camera through the terminal:

.. code-block:: console

  $ sudo raspi-config
  $ 5 Interfacing Options   Configure connections to peripherals
  $ P1 Camera       Enable/Disable connection to the Raspberry Pi Camera
  $ Would you like the camera interface to be enabled? <Yes>
  $ The camera interface is enabled. <OK>
  $ <Finish>

You will need to reboot after enabling the camera.

.. _quickstart guide: https://picamera.readthedocs.io/en/release-1.13/quickstart.html

Server Installation
===================
Coming soon..

Client Installation
===================
Coming soon..

.. _Raspbian: https://www.raspberrypi.org/downloads/raspbian/
