# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com

# --------------------------------------

import sys
import json
from datetime import datetime
from twilio.rest import TwilioRestClient

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)
    sys.stdout.write(error_msg)
    sys.stdout.flush()
    sys.exit()

account = settings["TWILIO_ACCOUNT"]
token = settings["TWILIO_TOKEN"]

client = TwilioRestClient(account, token)

client.messages.create(
    to="+12075136000",
    from_="+15106626969",
    body="py_sPi file cleanup job ran @ {}".format(datetime.now()),
)
