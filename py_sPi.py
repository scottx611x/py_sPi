# -*- coding: utf-8 -*-

import io
import os
import time
import random
from werkzeug.urls import url_fix
from datetime import datetime
from fractions import Fraction
from picamera import PiCamera
from PIL import Image
import twilio.twiml
from twilio.rest import TwilioRestClient

prior_image = None


class py_sPi(object):
    """
        Class that allows one to take stills, videos, and 
        instantiate a stream that will detect motion using 
        a raspberry pi and V2 Cam.

        Relies on some webserver running in the same dir and some port-forwarding
        so that twilio can make GET's for the images on whatever pi this runs on
    """
    camera = PiCamera()

    webserver_ip = "XXXXXXXXXXXX"
    webserver_port = "XXXXXXXXXXXX"

    account = "XXXXXXXXXXXX"
    token = "XXXXXXXXXXXX"
    client = TwilioRestClient(account, token)

    def __init__(self, day_or_night, resolution):

        self.camera_type = day_or_night
        self.picture_paths = []
        self.video_paths = []

        print(
            "\nInitializing {} camera...".format(self.camera_type))

        self.camera.resolution = resolution

        # Wait for the automatic gain control to settle
        time.sleep(3)

        """ 
        for low-light stills during the day
            # Set a framerate of 1/6fps, then set shutter
            # speed to 6s and ISO to 800
            self.camera.framerate = Fraction(1, 6)
            self.camera.shutter_speed = 6000000
            self.camera.exposure_mode = 'off'
            self.camera.iso = 800
            # Give the camera a good long time to measure AWB
            # (you may wish to use fixed AWB instead)
            time.sleep(10)
        """
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
