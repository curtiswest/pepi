import os
import sys
import subprocess
import logging
import datetime
import time
from future.utils import iteritems
import collections

import thriftpy
from thriftpy.rpc import client_context
import thriftpy.transport
import thriftpy.thrift
from flask import render_template, flash, url_for, request, redirect

from app import app
sys.path.append('../')
from server import ImageUnavailable, pepi_thrift

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '3.0'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'

str = type('')


def base_dir():
    """
    Gets the absolute file path based to the client folder
    """
    folder = os.path.dirname(os.path.realpath(__file__)).split('/')
    return '/'.join(folder[:-1])


def get_image_dir():
    """
    Get the directory to write an image to based on the current time
    """
    now = datetime.datetime.now()
    image_dir = base_dir() + "/images/" + datetime.datetime.strftime(now, '%Y%m%d%H%M%S')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    return image_dir


def open_images_folder():
    """
    Opens the `images` directory in the native file explorer, if supported
    """
    images_folder = base_dir() + '/images'
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    subprocess.call(["open", images_folder])


def find_server_by(servers, id_=None, ip=None):
    """
    Returns a server from the dictionary of servers that matches either the given `id_` or `ip.
    :param servers: a list of dictionaries of servers, with each being {id: id, ip: ip}
    :param id_: the id_ to match a server against
    :param ip: the ip to match a server against
    :return: the dictionary entry if a serve matches, None otherwise
    """
    for server in servers:
        if server['id'] == id_ or server['ip'] == ip:
            return server
    else:
        return None


def capture(all_servers, server_id='all'):
    """
    Sends the capture commands to the server given in `server_id` from the list
    of given servers (`all_servers`), else sends the capture command to all of
    the servers in `all_servers`.
    :param all_servers: a list of dictionaries of servers, with each being {id: id, ip: ip}
    :param server_id: the server_id to send to, or `all` for all servers
    :return: None
    """
    def _capture_single(server_):
        with client_context(pepi_thrift.CameraServer, server['ip'], 6000) as c:
            app.server_data[server_['id']].append(str(app.capture_no))
            c.start_capture(str(app.capture_no))

    if server_id != 'all':
        server = find_server_by(all_servers, id_=server_id)
        if server:
            _capture_single(server)
            app.capture_no += 1
        else:
            logging.warn("Couldn't find server with id: {}".format(server_id))
    else:
        # Capturing from all
        for server in all_servers:
            _capture_single(server)
        app.capture_no += 1


def download_images(all_servers):
    """
    Downloads all known images from servers in `all_servers` based on what the client has stored into a
    timestamped folder under '/images'.
    :param all_servers: a list of dictionaries of servers, with each being {id: id, ip: ip}
    :return: None
    """
    image_dir = get_image_dir()
    downloaded_images = collections.defaultdict(list)
    server_data = app.server_data.copy()

    for id_ in server_data:
        server = find_server_by(all_servers, id_=id_)
        if not server:
            downloaded_images[id_].extend(server_data[id_])
            continue
        with client_context(pepi_thrift.CameraServer, server['ip'], 6000, socket_timeout=10000) as c:
            for data_code in server_data[id_]:
                try:
                    images = c.retrieve_stills_jpg(data_code)
                except ImageUnavailable as e:
                    logging.warn(e)
                    downloaded_images[id_].append(data_code)
                else:
                    downloaded_images[id_].append(data_code)
                    for count, image in enumerate(images):
                        logging.info('Received data_code {}. Image length: {} bytes'.format(data_code, len(image)))
                        out_file = open('{}/id{}_d{}_cam{}.jpeg'.format(image_dir, server['id'], data_code, count),
                                        'wb')
                        out_file.write(image)
                        out_file.close()

    for id_, data_code_list in iteritems(downloaded_images):
        [server_data[id_].remove(data_code) for data_code in data_code_list]
    app.server_data = server_data
    logging.info('Client expected data codes now: {}'.format(app.server_data))


def identify_servers(servers):
    """
    Gets the identifier information about each server in the given `servers`
    dictionary, including its ID and stream urls and returns it as a list of dicts.
    :param servers: a list of IPs where servers are known to exist
    :return: a list of dictionaries containing {server_id: {ip: ip, id: id:, stream_url: stream_url}
    """
    out_servers = []
    for ip in servers:
        try:
            with client_context(pepi_thrift.CameraServer, ip, 6000, socket_timeout=2500) as c:
                stream_urls = c.stream_urls()
                # TODO: add multi-camera support for more than 1 stream per server
                stream_url = stream_urls[0] if stream_urls else []
                server_dict = {'ip': ip, 'id': c.identify(), 'stream_url': stream_url}
                out_servers.append(server_dict)
        except thriftpy.transport.TTransportException as e:
            logging.error(e)
        except Exception as e:
            logging.error(e)


    return out_servers


def shutdown(all_servers, server_id):
    """
    Shuts down the server given by `server_id` from the `all_servers` list, or if server_id
    is given as `all, shuts down all servers in the `all_servers` list.
    :param all_servers: a list of dictionaries of servers, with each being {id: id, ip: ip}
    :param server_id:
    :return:
    """
    def _shutdown_single(server_):
        with client_context(pepi_thrift.CameraServer, server_['ip'], 6000) as c:
            c.shutdown()

    if server_id != 'all':
        server = find_server_by(all_servers, id_=server_id)
        if server:
            _shutdown_single(server)
        else:
            logging.warn("Couldn't find server with id: {}".format(server_id))
    else:
        # Shutdown all all
        for server in all_servers:
            _shutdown_single(server)


@app.route('/', methods=['GET', 'POST'])
@app.route('/setup/', methods=['GET', 'POST'])
def index():
    """
    Displays a the main setup screen for PEPI and handles the button presses
    which call the above functions.
    :return: rendered Flask template.
    """
    # Get servers
    servers = identify_servers(app.heartbeater.ip_set.copy())

    # Handle POST requests from the page (e.g. a scan-network button press)
    if request.method == 'POST':
        for key in request.form.keys():
            if key == 'configure-all':
                flash('Configure All is not yet implemented in UI', 'warning')
                logging.debug('Configure All button pressed')
            elif key == 'open-capture-folder':
                logging.debug('Open Capture Folder button pressed')
                open_images_folder()
            elif key == 'capture':
                flash('Capture command sent to server(s). Images will be downloaded into Capture Folder '
                      'when server is ready', 'success')
                capture(all_servers=servers, server_id=request.form[key])
                time.sleep(1.5)  # Let the capture occur
            elif key == 'download':
                download_images(all_servers=servers)
                open_images_folder()
            elif key == 'stream':
                server = find_server_by(servers, id_=request.form[key])
                if server:
                    return redirect(url_for('stream', stream_url=server['stream_url'], server_id=server['id']))
            elif key == 'configure':
                flash('Configuring servers is not yet implemented in UI', 'warning')
                server = find_server_by(servers, id_=request.form[key])
                if server:
                    return redirect(url_for('configure', server_id=server['id']))
                pass
            elif key == 'shutdown':
                flash('Shutdown command sent to server(s). Servers will now shutdown', 'success')
                shutdown(all_servers=servers, server_id=request.form[key])
                pass

    # Render the template
    return render_template('/setup.html', title='Setup', servers=servers)


@app.route('/setup')
def configure(server_id):
    """
    Not implemented, but will be used to configure cameras.
    :return: rendered Flask template.
    """
    logging.warn('Got config for {} but config not yet implemented'.format(server_id))
    return render_template('/setup.html')


@app.route('/stream', methods=['GET'])
def stream():
    """
    Displays a full-screen stream for the given server.
    :return: rendered Flask template.
    """
    server_id = request.args.get('server_id')
    stream_url = request.args.get('stream_url')
    return render_template('/stream.html', title='Stream {}'.format(server_id), id_=server_id, stream_url=stream_url)
