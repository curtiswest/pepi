# PEPI

PEPI is a Python-based system that enables remote command and control of distributed servers with a connected camera, all from a local client. PEPI is used for the purposes of acquiring stereo-photogrammetry data and seamlessly supports any number of connected servers. The current implementation consists of three broad sections:
1. Client-side control software (including UI)
2. Server-side imaging software (responds to control command from client, such as taking an image)
3. Shared frameworks (primarily the communication framework adhered to by clients and servers)

## Getting Started
These instructions will get you a copy of the project up and running.
### Client-side
##### Hardware
The client software has been tested on Mac OS Sierra (10.12.5) with Python 2.7.13. In its current state, the software should be compatible with most Unix OS's out-of-the-box, and should be able to work on Windows with some small compatibility modifications, given the 'fragile' state of Python installations on Windows.

The client is connected over Ethernet to a wireless router that the servers are also connected to, such that the client is able to ping servers. Wifi connections have been tested to work as well, albeit with some inevitable latency introduced into the system -- it is up to the user if the introduced latency is acceptable.

##### Software
Instructions below are given for Unix OS. Windows will have slightly different notations.
1. Either download and extract the .zip of the repo, or git clone the latest version: `git clone git@bitbucket.org:cpizzolato/pibox.git`
2. CD into the directory: `cd pibox/client `
3. Install client-side requirements, which will install from requirements_common.txt too: `pip install -r requirements.txt`. (You may need to use `sudo`)
4. Make the client-side software executable: `sudo chmod u+x run.py`
5. Run the client-side software: `./run.py` or `python run.py`
6. Open your browser to [http://127.0.0.1:5000](http://127.0.0.1:5000) to bring up the user interface
7. Use the software! You will probably want to begin by entering the number of expected servers and clicking **Scan Network** to start the server client discovery process.

### Server-side
#### Hardware
The server software has been designed and tested on a Raspberry Pi 3 Model B equipped with a Raspberry Pi v1 Camera Module. The Raspberry Pi runs the lite version of Raspbian Jessie (essentially a stripped down Debian). Generally, it is easiest to just copy an image across to all server's SD cards rather than installing the software to each server individually.

It is possible to adapt the software for different cameras and running on different boards in a transparent manner, as long as the client receives the expected data, it will just work.

Some modification may be needed to use a v2 camera module to its full potential (primarily changing the specified resolution in `pepi_config.py` to the desired values). Future functionality may be implemented to detect the type of camera, if desired.

The Raspberry Pi's are connected wirelessly to a wireless router using the inbuilt wi-fi capabilities of the Pi 3. The Zero W should also be supported out-of-the-box, given its similar architecture and wireless capabilities, but this is untested. Ethernet should also be supported.

### Software

1. Setup Raspbian Jesse Lite on the server.
2. Setup SSH (public/private key based) to between the local client and the server.
3. SSH into the server with `ssh pi@<ip of the pi>`. You may need to use the option `ssh -i /path/to/ssh_key pi@<ip of the pi>` if your SSH key is not located in ~/.ssh
4. Either download and extract the .zip of the repo, or git clone the latest version: `git clone git@bitbucket.org:cpizzolato/pibox.git `.
4a. You may wish to place a copy of your SSH private key in /keys/pepi_rsa for the best compatibility with utility scripts (e.g. push to server dev scripts), but this is not required.
5. CD into `cd pibox/server`
6. Install server-side requirements, which will install from requirements_common.txt too: `pip install -r requirements.txt` (You may need to use `sudo`)
7. Make the client-side software executable: `sudo chmod u+x server.py`
8. Run the client-side software: `./server.py` or `python server.py`

## Running the tests
A test suite is included that covers the communication library and utilities.

#### Setting up for tests
1. Cd into `cd pibox/test`
2. Install test requirements: `pip install -r requirements.txt`
3. Run the test suite with `./run_tests.sh`, or manually by entering `nose2 --fail-fast --with-coverage --coverage-report html`. Note that you will see warnings output to the terminal log. This is expected, as the test cases cover 'bad' values as well as good, expected values. The bad values are hopefully caught by the software (generating the warning messages) and are dealt with.
4. A successful test will give the result similar to:
````bash
..........
----------------------------------------------------------------------
Ran 29 tests in 41.412s
OK
---------- coverage: platform darwin, python 2.7.13-final-0 ----------
Coverage HTML written to dir htmlcov
````
5. You can view the coverage report from  the `htmlcov` folder in your browser by executing `open htmlcov/index.html`.

## Built With
* [Python 2/3](https://www.python.org/) - This implementation is built on Python 2 and should be compatible (packages permitting) with Python 3 (untested). Python is not strictly required for software on either end, should the use of another language be desirable.
* [ZeroMQ](http://zeromq.org/) - The distributed message framework employed for communication between threads, processes and actual servers & clients over TCP.
* [Google Protocol Buffers](https://developers.google.com/protocol-buffers/) - Language & platform neutral framework upon which the messaging modules are built upon, allowing future expansion to the system if other languages/platforms are desired.
* [Picamera](https://picamera.readthedocs.io/) - Python package to access the Raspberry Pi camera modules.

## Authors & Acknowledgements

* **Claudio Pizzolato** - *Initial work and proof of concept*
* **Curtis West** - *Development from POC through to version 2.0*
* **Griffith University** - *Supporting the project*

## License

This project is licensed under Apache License 2.0. View the LICENSE file for details. 
