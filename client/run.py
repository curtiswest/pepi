#!/usr/bin/env python

import multiprocessing
import logging.config

import client

# Launch backend
logging.config.fileConfig('../setup/logging_config.ini')
backend = multiprocessing.Process(target=client.ClientBackend)
backend.daemon = True
backend.start()

# Launch frontend
from app import app
app.run(debug=False)
