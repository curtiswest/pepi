import os
import subprocess
import logging
import datetime

from flask import render_template, flash, url_for, request, redirect
from app import app
import thriftpy
poc_thrift = thriftpy.load('../poc.thrift', module_name='poc_thrift')
from thriftpy.rpc import client_context
import thriftpy.transport
import thriftpy.thrift

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

def find_server_by(servers, id=None, ip=None):
    for server in servers:
        if server['id'] == id or server['ip'] == ip:
            return server

def capture(all_servers, server_id):
    def _capture_single(server):
        with client_context(poc_thrift.ImagingServer, server['ip'], 6000) as c:
            app.server_data[server['id']].append(str(app.capture_no))
            c.start_capture(str(app.capture_no))

    if server_id != 'all':
        server = find_server_by(all_servers, id=server_id)
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
    image_dir = get_image_dir()
    downloaded_images = dict()

    for id in app.server_data:
        server = find_server_by(all_servers, id=id)
        with client_context(poc_thrift.ImagingServer, server['ip'], 6000, socket_timeout=10000) as c:

            for data_code in app.server_data[id]:
                try:
                    image = c.retrieve_still_jpg(data_code)
                except thriftpy.thrift.TApplicationException as e:
                    print(e)
                    pass
                else:
                    downloaded_images[id] = data_code
                    print('Image length: {} bytes'.format(len(image)))
                    out_file = open('{}/{}_{}.jpeg'.format(image_dir, server['id'], data_code), 'w')
                    out_file.write(image)
                    out_file.close()
                    # TODO delete the data code after use
    print('app.server_data: {}'.format(app.server_data))
    [app.server_data[id].remove(data_code) for id, data_code in downloaded_images.viewitems()]

def identify_servers(servers):
    out_servers = []
    for ip in servers:
        try:
            with client_context(poc_thrift.ImagingServer, ip, 6000, socket_timeout=100) as c:
                server_dict = {'ip': ip}
                server_dict['id'] = c.identify()
                server_dict['stream_url'] = c.stream_url()
                print(server_dict)
                out_servers.append(server_dict)
        except thriftpy.transport.TTransportException as e:
            pass
    return out_servers

def shutdown(all_servers, server_id):
    def _shutdown_single(server):
        with client_context(poc_thrift.ImagingServer, server['ip'], 6000) as c:
            c.shutdown()

    if server_id != 'all':
        server = find_server_by(all_servers, id=server_id)
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
    # Get servers
    server_dict = app.heartbeater.server_dict
    servers = identify_servers({k: v for k, v in server_dict.viewitems() if v == True})

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
            elif key == 'download':
                download_images(all_servers=servers)
                open_images_folder()
            elif key == 'stream':
                server = find_server_by(servers, id=request.form[key])
                if server:
                    return redirect(url_for('stream', stream_url=server['stream_url'], server_id=server['id']))
            elif key == 'configure':
                flash('Configuring servers is not yet implemented in UI', 'warning')
                pass
            elif key == 'shutdown':
                flash('Shutdown command sent to server(s). Servers will now shutdown', 'success')
                shutdown(all_servers=servers, server_id=request.form[key])
                pass

    # Render the template
    return render_template('/setup.html', title='Setup', servers=servers)

@app.route('/setup')
def configure(server_id):
    return render_template('/setup.html')

@app.route('/stream', methods=['GET'])
def stream():
    server_id = request.args.get('server_id')
    stream_url = request.args.get('stream_url')
    print('stream_url: {}'.format(stream_url))
    return render_template('/stream.html', title='Stream {}'.format(server_id), id_=server_id, stream_url=stream_url)
