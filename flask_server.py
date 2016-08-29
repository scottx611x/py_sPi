# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com
# --------------------------------------
# Flask server that will allow for the easy downloading of videos without
# them streaming their content in a mobile browser via use of the
# "Content-Disposition" header.

import json
from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)

# Grab some settings from our json config file
webserver_ip = settings["WEBSERVER_REMOTE_IP"]
webserver_port = settings["WEBSERVER_PORT"]


# This route will prompt a file download always
@app.route('/', methods=['GET'):
def get():
    # Set the right header for the response
    # to be downloaded, instead of just sent to the browser
    response.headers["Content-Disposition"] = "attachment;"
    return response

if __name__ == '__main__':
    app.run(
        host=webserver_ip,
        port=int(settings["WEBSERVER_PORT"]),
        debug=True
    )
