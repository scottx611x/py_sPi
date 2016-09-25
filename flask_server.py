# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com

# --------------------------------------
# Flask server that will allow for the easy downloading of videos without
# them streaming their content in a mobile browser

import sys
import time
import json
from flask import Flask, send_from_directory
from flask_api import status
from flask_compress import Compress

# Initialize the Flask application
app = Flask(__name__)

# Send jpegs and mp4s in a compressed format
app.config['COMPRESS_MIMETYPES'] = ['image/jpeg', 'video/mp4']
time.sleep(3)
Compress(app)

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)

# Grab some settings from our json config file
webserver_ip = settings["WEBSERVER_REMOTE_IP"]
webserver_port = settings["WEBSERVER_PORT"]


# This route will prompt a file download always
@app.route('/<filename>', methods=['GET'])
def send_file(filename):
    try:
        if '.mp4' in filename:
            return send_from_directory("vids", filename, as_attachment=True)
        if '.jpg' in filename:
            return send_from_directory("pics", filename, as_attachment=True)
    except Exception as e:
        sys.stdout.write(e)
        sys.stdout.flush()
        content = {'please move along': 'nothing to see here'}
        return content, status.HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(settings["WEBSERVER_PORT"]),
        threaded=True
    )
