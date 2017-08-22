#!/usr/bin/env bash

#sleep 15 # Delay on startup to let Pi stabilise


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "$DIR"
(cd "$DIR" && sudo python server.py)