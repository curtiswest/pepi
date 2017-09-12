#!/usr/bin/env python

from collections import defaultdict

from app import app
import heartbeater
from server import IPTools

app.heartbeater = heartbeater.Heartbeater(min_interval=5, base_ip=IPTools.get_subnet_from(IPTools.current_ips()[0]))
app.heartbeater.start()
app.server_data = defaultdict(list)
app.capture_no = 1
app.run(debug=False, host="0.0.0.0")
