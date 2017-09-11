.. _installation:

============
Installation
============

.. note::
  These installation notes are mainly for the provided PEPI implementations, running on the specified :ref:`hardware`. Configurations outside this scope may require different setup steps.

.. _Prerequisites:

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

If you have an old version, or you get errors about Python not being recognised, you should follow the `Python Install Guide`_

.. _Python Install Guide: https://wiki.python.org/moin/BeginnersGuide/Download

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
#. Create a new file in the root of the SD card called exactly ``ssh``, **without any file extension** to enable SSH by default on this SD card.

.. _Raspbian: https://www.raspberrypi.org/downloads/raspbian/

Configuring Wi-Fi
~~~~~~~~~~~~~~~~~
#. Open your file exporer to the root of your flashed SD card.
#. Create a new file called ``wpa_supplicant.conf``, containing the following details.  Replace SSID and PASSWORD with your intended wireless network's details (keep the quotes).

   .. code-block:: text

     network={
      ssid="SSID"
      psk="PASSWORD"
     }

#. Save the file back to the SD card and eject the card.

Camera Module
-------------
The included server implementation (:py:mod:`raspi_server`) needs a properly installed and configured Raspberry Pi Camera Module.

PiCamera has provided a great `quickstart guide`_ on this process. However, if you are using SSH (ie. a terminal) to connect to your Raspberry Pi, you cannot complete the last steps in that guide as it requires a GUI.

To enable the camera through the terminal:

.. code-block:: console

  $ sudo raspi-config
  5 Interfacing Options   Configure connections to peripherals
  P1 Camera       Enable/Disable connection to the Raspberry Pi Camera
  Would you like the camera interface to be enabled? <Yes>
  The camera interface is enabled. <OK>
  <Finish>

You'll need to reboot after enabling the camera.

.. _quickstart guide: https://picamera.readthedocs.io/en/release-1.13/quickstart.html

.. _SSH Keys:

SSH Keys
--------
You may wish to look into using SSH keys. This removes the need to type in a password when logging into the Pi over SSH -- something that gets very annoying when you're wrangling dozens of them.

If you use SSH keys alongside the Raspberry Pi server implementation, you can place a copy of your private key in your cloned Git repo under ``/raspi_server/keys``. This will allow you to use the provided utility scripts to push out new versions to all servers at once, which is super useful for development work.

While we recommend using a new SSH key-pair for PEPI with the name given below, it's not mandatory but you will need modify the utility scripts.

You can generate a new SSH key from most Unix terminals with:

.. code-block:: console

   $ ssh-keygen -t rsa -C "PEPI SSH Key"

You'll be asked to save the SSH key - save it somewhere easy like your home folder under the name pepi_rsa: ``~/pepi_rsa``.

Now the problem is getting the SSH private key onto your Pi's. The easiest way is to use SSH itself (with a password this time):

.. code-block:: console

   $ cat ~/pepi_rsa.pub | ssh pi@<IP-ADDRESS> 'cat >> .ssh/authorized_keys'

You should now be able to SSH into the Pi without a password (you may be prompted about an unknown host, this is expected for the first usage):

.. code-block:: console

   $ ssh -i /path/to/your/pepi_rsa pi@<IP-ADDRESS>

Client Installation
===================
#. Clone the Git repo to get the latest version of the PEPI client:

   .. code-block:: console

      $ cd ~
      $ git clone https://github.com/curtiswest/pepi.git
      $ cd pepi
      $ ls
      LICENSE      README.rst   client       poc.thrift   raspi_server server       test         unittest.cfg

#. Install the client's Python dependencies:

   .. code-block:: console

      $ python --version
      Python 2.7.13 (or Python 3.6.1)
      $ cd client/
      $ sudo pip install -r requirements.txt

#. Make the client executable:

   .. code-block:: console

      $ chmod +x run.py

#. Run the client using either of the commands below:

   .. code-block:: console

      $ python run.py
      INFO:werkzeug: * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
      $ ./run.py
      INFO:werkzeug: * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

#. Open your internet browser to `<http://0.0.0.0:5000/>`_ and you should see the PEPI user interface. See :ref:`Using PEPI <using-pepi>` to learn more about this interface.

Raspberry Pi Server Installation
================================

.. note::
  Make sure you've followed the relevant steps in the `Prerequisites`_ section above before proceeding.

Setting up your first Pi is the slowest. After one is set up, you can simply :ref:`duplicate that SD card <flash cards>`.

Downloading & Installing
------------------------

Firstly, we need to obtain the software:

#. SSH into your pi, e.g. ``ssh pi@<IP-ADDRESS>`` or if using `SSH Keys`_ (recommended), ``ssh -i /path/to/pepi_rsa pi@<IP-ADDRESS>``
#. Clone the latest version of the software from Git

   .. code-block:: console

      $ cd ~
      $ git clone https://github.com/curtiswest/pepi.git
      $ cd pepi
      $ ls
      LICENSE      README.rst   client       poc.thrift   raspi_server server       test         unittest.cfg

Alternatively, if your Pi does not have internet access, you could download a `.zip of the repo` and use a flash drive to transfer it to the Pi.

.. _.zip of the repo: https://github.com/curtiswest/pepi/archive/master.zip

#. Place a copy of your SSH key in the ``raspi_server/keys`` folder if you want to use the utility scripts:

   .. code-block:: console

      $ cp /path/to/your/pepi_rsa raspi_server/keys

#. Install the server's requirements.

   .. code-block:: console

      $ python --version
      Python 2.7.13 (or Python 3.6.1)
      $ cd raspi_server/
      $ sudo pip install -r requirements.txt

#. Test that the server can launch:

   .. code-block:: console

      $ python server.py
      INFO:root:Starting RaspPiImagingServer

#. If you see the above, then the server is working fine. Stop the server with ``CTRL + C``.
#. Now, we need to setup launching the software on boot. A script is included, ``raspi_server/start_on_boot.sh``, that handles everything needed to launch the server (from the correct directory context etc). You can add this to the Pi's boot sequence by executing the following:

   .. code-block:: console

      $ cd ..
      $ pwd
      /home/pi/pepi
      $ sudo sed -i -e '$i \bash /home/pi/pepi/raspi_server/start_on_boot.sh &\n' /etc/rc.local


#. Reboot your Pi with:

   .. code-block:: console

      $ sudo shutdown -r now

#. The server should have started running automatically on boot. You can check this by looking for the ``run.py`` process:

   .. code-block:: console

      $ ssh -i /path/to/pepi_rsa pi@<IP-ADDRESS>
      $ ps aux | grep run.py
      root       740  1.5  2.5 120552 22388 ?        Sl   20:58   0:02 python run.py

#. If everything works, congratulations! If not, try walking through these steps and double-checking the commands were entered correctly. Perhaps try checking that your script was added to the boot script correctly (sometimes you may need special permissions to edit the /etc/rc.local file) with:

   .. code-block:: console

      $ cat /etc/rc.local | tail -5
      fi

      bash /home/pi/pepi/raspi_server/start_on_boot.sh &

      exit 0

.. _flash cards:

Duplicating SD cards
--------------------

.. warning::
  You will be reading and writing from raw disk partitions. **You could erase your computer** if you execute the commands below with the wrong parameters. Double-check your commands before executing.

.. note::
  It is untested whether these image files are compatible across the different Raspberry Pi Models. That is to say, it is unclear whether a Raspberry Pi 3 image can be cloned onto an SD card intended for a Raspberry Pi Zero. If you try this, please update this documentation with the results and create a `pull request`_.

.. _pull request: https://github.com/curtiswest/pepi/compare

Once you've verified that the card works exactly how you want, you can make an image of the SD card that will allow you to duplicate it onto other SD cards.

#. Insert the card into your card reader.
#. Find where the card is mounted by running ``diskutil list``. Look for the device that matches your SD card, generally by the size of the disk is easiest. Here, a 8GB SD card is inserted and appears under ``/dev/disk2/``.

   .. code-block:: console

      $ diskutil list
      /dev/disk0 (internal, physical):
         #:                       TYPE NAME                    SIZE       IDENTIFIER
         0:      GUID_partition_scheme                        *121.3 GB   disk0
         2:          Apple_CoreStorage Macintosh HD            120.5 GB   disk0s2
      /dev/disk2 (internal, physical):
         #:                       TYPE NAME                    SIZE       IDENTIFIER
         0:     FDisk_partition_scheme                        *7.9 GB     disk2
         1:             Windows_FAT_32 boot                    43.7 MB    disk2s1
         2:                      Linux                         7.9 GB     disk2s2

#. Remember the ``/dev/diskx/`` (where x = your disk's number, which above would be ``/dev/disk2/``) location where you SD card is mounted.
#. Run the following command to unmount any mounted SD card partitions:

   .. code-block:: console

      $ df -H
      Filesystem      Size   Used  Avail Capacity iused      ifree %iused  Mounted on
      /dev/disk1     112Gi   69Gi   42Gi    62% 1354336 4293612943    0%   /
      /dev/disk2s1    41Mi   21Mi   20Mi    51%       0          0  100%   /Volumes/boot
      $
      $ sudo umount /dev/diskx*
      $ df -H
      Filesystem      Size   Used  Avail Capacity iused      ifree %iused  Mounted on
      /dev/disk1     112Gi   69Gi   42Gi    62% 1354336 4293612943    0%   /

#. Now, we can image the SD card with the ``dd`` command:

   .. code-block:: console

      $ dd if=/dev/diskx/ of=~/rpi.img bs=4M
      $ ls -la ~/ | grep rpi.img
      -rw-r--r--   1 root        staff  7948206080 20 Aug 23:23 rpi.img
      $ sudo sync

   The ``rpi.img`` file contains a complete copy of the SD card. It is possible to shrink the image to copy it quicker using a `GParted`_ live boot disk, but you'll need to expand it again once copied across. If you have lots of cards to duplicate, you could look into building a `Open Source Image Duplicator`_ to allow you to duplicate several at a time.

.. _GParted: https://gparted.org/
.. _Open Source Image Duplicator: https://github.com/rockandscissor/osid/

#. Eject that SD card, and insert the new SD card you want to setup.
#. Locate where that disk is located (usually, it's the same--but not always!), in this case ``/dev/disk2/``:

   .. code-block:: console

      $ diskutil list
      /dev/disk0 (internal, physical):
         #:                       TYPE NAME                    SIZE       IDENTIFIER
         0:      GUID_partition_scheme                        *121.3 GB   disk0
         2:          Apple_CoreStorage Macintosh HD            120.5 GB   disk0s2
      /dev/disk2 (internal, physical):
         #:                       TYPE NAME                    SIZE       IDENTIFIER
         0:             Windows_FAT_32                        *7.9 GB     disk2

#. Unmount the new SD card, if it has any mounted partitions:

   .. code-block:: console

      $ sudo umount /dev/diskx*

#. Now we can copy the image back onto the SD card by simply reversing the ``dd`` command (notice the ``if`` and ``of`` arguments are now reversed):

   .. code-block:: console

      $ dd if=~/rpi.img of=/dev/diskx/ bs=4M
      $ sudo sync

#. Eject the SD card, and repeat the above 3 steps for as many cards as you need. You should be able to put these cards directly into new Raspberry Pi's and have them work just as the first did.
