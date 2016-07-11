# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com


import cv2
import sys
import time
from werkzeug.urls import url_fix
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
from twilio.rest import TwilioRestClient

prior_image = None


class py_sPi(object):
    """
        Class that allows one to instantiate a stream that will detect motion using
        a raspberry pi and V2 Cam.

        NOTE: This relies on some webserver running in the same dir and some port-forwarding
        so that twilio can make GET's for the images on whatever pi this runs on.

        Python's SimpleHTTPServer works great for this.
    """
    camera = PiCamera()

    webserver_ip = "XXXXXXXXXXXX"
    webserver_port = "XXXXXXXXXXXX"

    account = "XXXXXXXXXXXX"
    token = "XXXXXXXXXXXX"
    client = TwilioRestClient(account, token)

    def __init__(self, framerate, resolution):

        print("\nCamera initializing")
        self.camera.framerate = framerate
        self.camera.resolution = resolution

        self.rawCapture = PiRGBArray(self.camera, size=resolution)

        # Wait for the automatic gain control to settle
        time.sleep(5)

        self.avg = None
        self.min_save_seconds = 5
        self.lastSaved = datetime.now()
        self.motionCounter = 0
        self.min_motion_frames = 45
        self.min_area = 5000

        print("\nCamera initialized")

    def detect_motion(self):
        global prior_image
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        if prior_image is None:
            prior_image = Image.open(stream)
        else:
            current_image = Image.open(stream)
            if current_image != prior_image:
                print("\nMotion detected")

                current_image_path = self.make_picture_path(datetime.now())
                current_image.save(current_image_path)
                print(
                    "\nWrote {} to disk.".format(current_image_path))
                prior_image = current_image

                self.send_mms(current_image_path)
                print("\nSleeping 30 secs")
                time.sleep(30)

    def take_picture(self, pictures_to_take):
        while pictures_to_take:
            time.sleep(3)
            self.camera.capture(self.make_picture_path(datetime.now()))
            self.picture_paths += [pic_path]
            pictures_to_take -= 1
            print("\nWrote {} to disk.".format(pic_path))
            self.send_mms(pic_path)

    def take_video(self, duration):
        vid_path = '{}.h264'.format(datetime.now())
        self.camera.start_recording(vid_path)
        time.sleep(duration)
        self.camera.stop_recording()
        print("\nWrote {} to disk.".format(vid_path))

    def send_mms(self, picture_path):
        print("\nSending mms")
        message = self.client.messages.create(
            to="XXXXXXXXXXXX",
            from_="XXXXXXXXXXXX",
            body="XXXXXXXXXXXX",
            media_url=["http://{}:{}/{}".format(
                self.webserver_ip,
                self.webserver_port,
                url_fix(picture_path))]
        )

    def make_picture_path(self, timestamp):
        return'{}.jpg'.format(timestamp)

cam = py_sPi("daytime", (3280, 2464))


while True:
    cam.detect_motion()
