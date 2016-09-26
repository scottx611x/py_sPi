<h2><img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/cb/Raspberry_Pi_Logo.svg/810px-Raspberry_Pi_Logo.svg.png" height="25px" width="20px" />py_sPi  &nbsp; <a href="https://travis-ci.org/scottx611x/py_sPi"><img src="https://api.travis-ci.org/scottx611x/py_sPi.svg"/></a> &nbsp; <a href="https://codecov.io/gh/scottx611x/py_sPi">
  <img src="https://codecov.io/gh/scottx611x/py_sPi/branch/master/graph/badge.svg" alt="Codecov" />
</a></h2> 

Surveillance system using a RaspberryPi and V2 Camera in python

Example message:

<img src="https://cloud.githubusercontent.com/assets/5629547/18835625/01c33b24-83ca-11e6-893d-be401a0e6ec9.jpg" height="500px" />

##TO-DO:
- [ ] Move more configurables into config.json
- [ ] More tests & fix codecov
- [ ] Utilize: ` with picamera.PiCamera() as camera:`
- [ ] find pid of python scripts & kill them rather than `killall pyhton`
- [ ] Fetch a remote script to automate install process & fetching of dependencies
  - **NOTE**: Pi-hole does: `curl -L https://install.pi-hole.net | bash`
- [ ] [Dockerize](https://github.com/umiddelb/armhf/wiki/Get-Docker-up-and-running-on-the-RaspberryPi-(ARMv6)-in-four-steps-(Wheezy))




