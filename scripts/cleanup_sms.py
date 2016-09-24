from twilio.rest import TwilioRestClient

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)

account = settings["TWILIO_ACCOUNT"]
token = settings["TWILIO_TOKEN"]

client = TwilioRestClient(account, token)

message = self.client.messages.create(
                to="+12075136000",
                from_="+15106626969",
                body="py_sPi file cleanup job ran @ {}".format(datetime.now()),
            )
