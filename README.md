<h2><img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/cb/Raspberry_Pi_Logo.svg/810px-Raspberry_Pi_Logo.svg.png" height="25px" width="20px" />py_sPi</h2>

Surveillance system using a RaspberryPi and V2 Camera in python

##TO-DO:
[picamera docs](https://picamera.readthedocs.io/en/release-1.12/)
[combat shadows/lightchanges from being detected as motion](http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/)
[combat shadows/lightchanges from being detected as motion](http://shallowsky.com/software/motioncam.html)
- [ ] Check for current free disk space, and delete old pics if necessary (or just delete anything over a week old)
- [ ] Utilize: ` with picamera.PiCamera() as camera:`
- [ ] run a Flask server instead of python's SimpleHTTPServer to allow the association of `Content-Disposition` header to force download instead of stream
- [ ] run day/night cam based on light levels
- [ ] start `run.sh` in a crontab on every reboot (add rm -rf on `nohup.out`)
- [ ] add a `requirement.txt` file
- [ ] Figure out how to not detect moving shadows/branches as motion (maybe have some type of way to learn the enviornment???)-
- [ ] leverage pi thats not in use to do the `.h264` to `.mp4` conversion
- [ ] Fetch a remote script to automate install process & fetching of dependencies
  - **NOTE**: Pi-hole does: `curl -L https://install.pi-hole.net | bash`
- [ ] [Containerize... Conda? Docker?](https://github.com/umiddelb/armhf/wiki/Get-Docker-up-and-running-on-the-RaspberryPi-(ARMv6)-in-four-steps-(Wheezy))
- [x] [Recognize camera & take a ](https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera)[**test pic**](https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md)
- [x] Figure out which resolutions work the best for this use case (can MMS be of a certain size or below??? Do high-res stills require too much `gpu_mem` to be allocated???)
- [x] Different settings for `iso`, `exposure`, `shutter_speed` and others to take better pics in low light (Shouldn't be necessary when both cams are running)
- [x] Provide options to `py_Spi.__init__` for the Normal cam and the NoIR Cam
- [x] Get motion detection working
- [x] Create way to find % difference between stills when motion is detected (don't want too easy of a trigger)
- [x] [Leverage Twilio to send MMS](https://www.twilio.com/docs/libraries/python)
- [x] Run some lightweight webserver allowing for twilio to make GET's on the images we want
  - Make the proper GET's (can probably send multiple pics in one message See [`media_url`](https://www.twilio.com/docs/quickstart/python/sms/sending-via-rest))
- [x] Send link to video in message as well!
- [x] Utilize a config file
- [x] Figure out sunrise/sunset and alternate between booting Pi w/ IR cam and Pi w/ daytime cam (Shouldn't be necessary, Cameras wont detect motion if too dark or too light)
