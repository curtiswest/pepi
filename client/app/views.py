import sys
import os
import subprocess
import logging

from flask import render_template, flash, url_for, request, redirect
from app import app

sys.path.append('../')
from communication.communication import CommunicationSocket
from communication.pymsg import InprocMessage, WrapperMessage

def open_images_folder():
    folder = os.path.dirname(os.path.realpath(__file__)).split('/')
    base_folder = '/'.join(folder[:-1])
    images_folder = base_folder + '/images'
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    subprocess.call(["open", images_folder])

@app.route('/', methods=['GET', 'POST'])
@app.route('/setup/', methods=['GET', 'POST'])
def index():
    if not app.debug:
        # Connect to the ClientBackend over ipc connection
        socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        socket.connect_to('ipc://ui.pipe')

        # Get the status of the servers from ClientBackend for displaying
        msg = InprocMessage(msg_req='server_status').wrap()
        socket.send(msg.serialize())
        data = socket.receive()
        msg = WrapperMessage.from_serialized_string(data).unwrap()
        if isinstance(msg, InprocMessage):
            servers = msg.list_of_dicts
        else:
            servers = []
    else:
        # Dummy debug data
        servers = [
            {'ip': '10.0.0.1', 'id': '0000ffffaaaabbbb', 'alive': True},
            {'ip': '10.0.0.2', 'id': '0000aaaaaaaaaaaa', 'alive': True},
            {'ip': '10.0.0.3', 'id': '0000bbbbbbbbbbbb', 'alive': False},
            {'ip': '10.0.0.4', 'id': '0000cccccccccccc', 'alive': True}
        ]

    # Handle POST requests from the page (e.g. a scan-network button press)
    if request.method == 'POST':
        for key in request.form.keys():
            if key == 'scan-network':
                flash('Network scan started', 'success')
                try:
                    num_servers = int(request.form['expected'])
                    msg = InprocMessage('rescan {}'.format(num_servers))
                    socket.send(msg.wrap().serialize())
                    logging.debug('Sending send-network message: {}'.format(msg))
                except KeyError:
                    logging.warn('Attempted to send-network message, but not given # of expected servers. Aborting..')
                except ValueError:
                    logging.warn('Number of expected servers is somehow not an integer')
            elif key == 'configure-all':
                flash('Configure All is not yet implemented in UI', 'warning')
                logging.debug('Configure All button pressed')
            elif key == 'open-capture-folder':
                logging.debug('Open Capture Folder button pressed')
                open_images_folder()
            elif key == 'capture':
                flash('Capture command sent to server(s). Images will be downloaded into Capture Folder '
                      'when server is ready', 'success')
                logging.warn('Capture button pressed. Value: {}'.format(request.form[key]))
                try:
                    msg = InprocMessage('capture {}'.format(request.form[key]))
                except KeyError:
                    logging.warn('Error in sending capture command - no server ID given to capture from')
                else:
                    logging.debug('Sending capture message: {}'.format(msg))  # DEBUG
                    socket.send(msg.wrap().serialize())
            elif key =='download':
                try:
                    msg = InprocMessage('download {}'.format(request.form[key]))
                except KeyError:
                    logging.warn('Error in sending download command - no server ID given to download from')
                else:
                    logging.debug('Sending download message: {}'.format(msg))  # DEBUG
                    socket.send(msg.wrap().serialize())
                open_images_folder()
            elif key == 'stream':
                for server in servers:
                    if request.form[key] == server['id']:
                        return redirect(url_for('stream', server_id=server['id'], ip=server['ip']))
                else:
                    logging.error('Got stream button for a non-existent server?')
            elif key == 'configure':
                flash('Configuring servers is not yet implemented in UI', 'warning')
                logging.debug('Configure Button pressed for server {}'.format(request.form[key]))
                # return redirect(url_for('configure', server_id=request.form[key]))
            elif key == 'shutdown':
                flash('Shutdown command sent to server(s). Servers will now shutdown', 'success')
                logging.warn('Shutdown button pressed. Value: {}'.format(request.form[key]))
                try:
                    msg = InprocMessage('shutdown {}'.format(request.form[key]))
                except KeyError:
                    logging.warn('Error in sending shutdown command - no server ID given to shutdown')
                else:
                    logging.debug('Sending shutdown message: {}'.format(msg))  # DEBUG
                    socket.send(msg.wrap().serialize())
                # flash('Shutdown All is not yet implemented in UI', 'warning')

    # Render the template
    return render_template('/setup.html', title='Setup', servers=servers)

@app.route('/setup')
def configure(server_id):
    return render_template('/setup.html')

@app.route('/stream', methods=['GET'])
def stream():
    server_id = request.args.get('server_id')
    ip = request.args.get('ip')
    return render_template('/stream.html', title='Stream {}'.format(server_id), id_=server_id, ip=ip)