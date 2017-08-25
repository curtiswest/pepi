#!/usr/bin/env python

from app import app
import heartbeater
from collections import defaultdict

app.heartbeater = heartbeater.Heartbeater(min_interval=5, base_ip='10.0.0.')
app.heartbeater.start()
app.server_data = defaultdict(list)
app.capture_no = 1
app.run(debug=True, host="0.0.0.0")
