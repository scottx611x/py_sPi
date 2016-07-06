# py_sPi
Surveillance system using a RaspberryPi and V2 Camera in python

##TO-DO:

- [x] [Recognize camera & take a ](https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera)[**test pic**](https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md)
- [ ] Check for current free disk space, and delete old pics if necessary
- [ ] Get motion detection working
- [ ] [Leverage Twilio to send MMS](https://www.twilio.com/docs/libraries/python)
- [ ] [Run a flask server to accept incoming texts](https://github.com/scottx611x/Website/blob/master/scripts/python/sms_automation.py#L31)
  - Example: `"Motion was detected (5) times today. Would you like to see the pictures [Y/N]?"`
- [ ] Figure out sunrise/sunset and alternate between Pi w/ IR cam and Pi w/ daytime cam
- [ ] Fetch a remote script to automate install process
  - **NOTE**: Pi-hole does: `curl -L https://install.pi-hole.net | bash`
- [ ] [Containerize](https://github.com/umiddelb/armhf/wiki/Get-Docker-up-and-running-on-the-RaspberryPi-(ARMv6)-in-four-steps-(Wheezy))

