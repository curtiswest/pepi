import sys
import os
import subprocess
import logging

from flask import render_template, flash, url_for, request, redirect
from app import app

sys.path.append('../')
from communication.communication import CommunicationSocket
from communication.pymsg import InprocMessage, WrapperMessage

@app.route('/', methods=['GET', 'POST'])
@app.route('/setup/', methods=['GET', 'POST'])
def index():
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

    # Handle requests from the page (e.g. a scan-network button press)
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
                folder = os.path.dirname(os.path.realpath(__file__)).split('/')
                base_folder = '/'.join(folder[:-1])
                images_folder = base_folder + '/images'
                if not os.path.exists(images_folder):
                    os.makedirs(images_folder)
                subprocess.call(["open", images_folder])
            elif key == 'capture':
                flash('Capture command sent to server(s). Images will be downloaded into Capture Folder '
                      'when server is ready', 'success')
                logging.debug('Capture button pressed')
                try:
                    msg = InprocMessage('capture {}'.format(request.form[key]))
                except KeyError:
                    logging.warn('Error in sending capture command - no server ID given to capture from')
                else:
                    logging.debug('Sending capture message: {}'.format(msg))  # DEBUG
                    socket.send(msg.wrap().serialize())
            elif key == 'stream':
                flash('Streaming not yet implemented in UI', 'warning')
                logging.debug('Stream button pressed for server {}'.format(request.form[key]))
            elif key == 'configure':
                flash('Configuring servers is not yet implemented in UI', 'warning')
                logging.debug('Configure Button pressed for server {}'.format(request.form[key]))
                return redirect(url_for('configure', server_id=request.form[key]))
            elif key == 'shutdown-all':
                flash('Shutdown All is not yet implemented in UI', 'warning')

    # Render the template
    return render_template('/setup.html', title='Setup', servers=servers)

@app.route('/setup/<server_id>')
def configure(server_id):
    print('Server ID is: {}'.format(server_id))  # DEBUG
    return render_template('/setup.html', title=server_id)