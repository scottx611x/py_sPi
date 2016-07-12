<h2><img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/cb/Raspberry_Pi_Logo.svg/810px-Raspberry_Pi_Logo.svg.png" height="25px" width="20px" />py_sPi</h2>

Surveillance system using a RaspberryPi and V2 Camera in python

##TO-DO:
[picamera docs](https://picamera.readthedocs.io/en/release-1.12/)
  
- [x] [Recognize camera & take a ](https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera)[**test pic**](https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md)
- [ ] Figure out which resolutions work the best for this use case (can MMS be of a certain size or below??? Do high-res stills require too much `gpu_mem` to be allocated???)
- [ ] Utilize: ` with picamera.PiCamera() as camera:`
- [ ] Check for current free disk space, and delete old pics if necessary
- [x] Get motion detection working
- [x] Create way to find % difference between stills when motion is detected (don't want too easy of a trigger)
- [x] [Leverage Twilio to send MMS](https://www.twilio.com/docs/libraries/python)
- [ ] [Run some lightweight webserver to accept incoming texts as well as allowing for twilio to make GET's on the images we want](https://github.com/scottx611x/Website/blob/master/scripts/python/sms_automation.py#L31)
  - Example: `"Motion was detected (5) times today. Would you like to see the pictures [Y/N]?"`
  - If yes, make the proper GET's (can probably send multiple pics in one message See [`media_url`](https://www.twilio.com/docs/quickstart/python/sms/sending-via-rest))
- [ ] Figure out sunrise/sunset and alternate between booting Pi w/ IR cam and Pi w/ daytime cam
- [ ] Fetch a remote script to automate install process & fetching of dependencies
  - **NOTE**: Pi-hole does: `curl -L https://install.pi-hole.net | bash`
- [ ] [Containerize... Conda? Docker?](https://github.com/umiddelb/armhf/wiki/Get-Docker-up-and-running-on-the-RaspberryPi-(ARMv6)-in-four-steps-(Wheezy))

