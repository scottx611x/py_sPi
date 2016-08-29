# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com

import os
import cv2
import sys
import time
import json
import uuid
import zipfile
from werkzeug.urls import url_fix
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
from twilio.rest import TwilioRestClient


try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)


class py_sPi(object):

    """
        Class that allows one to instantiate a stream that will detect motion using
        a raspberry pi and V2 Cam.

        NOTE: This relies on some webserver running in the same dir and some port-forwarding
        so that twilio can make GET's for the images on whatever pi this runs on.

        Flask works great for this.
    """

        camera = PiCamera()

    webserver_ip = settings["WEBSERVER_REMOTE_IP"]
    webserver_port = settings["WEBSERVER_PORT"]

    account = settings["TWILIO_ACCOUNT"]
    token = settings["TWILIO_TOKEN"]
    client = TwilioRestClient(account, token)

    def __init__(self, framerate, resolution):

        message = self.client.messages.create(
            to="+12075136000",
            from_="+15106626969",
            body="py_sPi is starting @ {}".format(datetime.now()),
        )
        sys.stdout.write("\nCamera initializing")
        sys.stdout.flush()

        self.camera.framerate = framerate
        self.camera.resolution = resolution
        sys.stdout.write("\nStarting raw capture")
        sys.stdout.flush()

        self.rawCapture = PiRGBArray(self.camera, size=resolution)

        # Wait for the automatic gain control to settle
        time.sleep(5)

        self.avg = None
        self.video_duration = 10
        self.lastSaved = datetime.now()
        self.motionCounter = 0

        self.min_motion_frames = 3
        self.delta_threshold = 10
        self.min_area = 7500

        sys.stdout.write("\nCamera initialized")
        sys.stdout.flush()

    def detect_motion(self):
        sys.stdout.write("\nDetecting Motion")
        sys.stdout.flush()
        # capture frames from the camera
        for f in self.camera.capture_continuous(self.rawCapture, format="bgr",
                                                use_video_port=True):
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and MOTION/NO_MOTION text
            frame = f.array
            timestamp = datetime.now()
            text = "NO_MOTION"

            # resize the frame, convert it to grayscale, and blur it
            # frame = imutils.resize(frame, width=self.resolution[0])
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the "average" frame is None, initialize it
            if self.avg is None:
                self.avg = gray.copy().astype("float")
                self.rawCapture.truncate(0)
                continue

            # accumulate the weighted average between the current frame and
            # previous frames, then compute the difference between the current
            # frame and running average
            cv2.accumulateWeighted(gray, self.avg, 0.5)
            frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frame_delta, self.delta_threshold, 255,
                                   cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self.min_area:
                    continue

                # compute the bounding box for the contour, draw it on the
                # frame, and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "MOTION DETECTED"

            # draw the text and timestamp on the frame

            cv2.putText(frame, "Motion Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, str(datetime.now()), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

            # check to see if motion has been detected
            if text == "MOTION DETECTED":

                # check to see if enough time has passed between uploads
                if (timestamp - self.lastSaved).seconds >=  \
                        self.video_duration:
                    # increment the motion counter
                    self.motionCounter += 1

                    # check to see if the number of frames with consistent
                    # motion is high enough
                    if self.motionCounter >= self.min_motion_frames:
                        # write the image to disk
                        pic_path = self.make_picture_path(datetime.now())

                        cv2.imwrite(pic_path, frame)

                        # send_mms
                        sys.stdout.write(
                            "\nMotion detected!!! Recording a {} second clip".format(self.video_duration))
                        sys.stdout.flush()
                        vid_path = self.take_video(self.video_duration)

                        self.send_mms(pic_path, vid_path)

                        # update the last uploaded timestamp and reset the
                        # motion counter
                        self.lastSaved = timestamp
                        self.motionCounter = 0

            # otherwise, the room is not MOTION
            else:
                self.motionCounter = 0

            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)

    def take_video(self, duration):
        sys.stdout.write("\nTaking Video")
        sys.stdout.flush()
        vid_path = 'vids/{}.h264'.format(uuid.uuid4())
        self.camera.start_recording(vid_path)
        time.sleep(duration)
        self.camera.stop_recording()
        sys.stdout.write("\nWrote {} to disk.".format(vid_path))
        sys.stdout.flush()
        new_vid_path = vid_path.replace(".h264", ".mp4")
        return new_vid_path
        try:
            os.system("MP4Box -add {} {}".format(vid_path, new_vid_path))
            os.remove(vid_path)
        except Exception as e:
            return None

    def send_mms(self, picture_path, video_path):
        sys.stdout.write("\nSending MMS message")
        sys.stdout.flush()
        body = ""
        # numbers = ["+12075136000", "+12077547135"]
        numbers = ["+12075136000"]

        if video_path:
            body = "Motion detected! Video link: {}".format(
                self.make_twilio_url(video_path))
        else:
            body = "Motion detected!"

        for number in numbers:
            message = self.client.messages.create(
                to=number,
                from_="+15106626969",
                body=body,
                media_url=["{}".format(
                    self.make_twilio_url(picture_path))]
            )

    def make_picture_path(self, timestamp):
        return 'pics/{}.jpg'.format(timestamp).replace(" ", "_")

    def make_twilio_url(self, path):
        return "http://{}:{}/{}".format(
            self.webserver_ip,
            self.webserver_port,
            url_fix(path))


cam = py_sPi(30, (1920, 1080))

cam.detect_motion()
