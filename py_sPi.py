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

        # assign framerate and resolution
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
        # Capture continuous video frames
        for f in self.camera.capture_continuous(self.rawCapture, format="bgr",
                                                use_video_port=True):
            # grab raw numpy array
            frame = f.array
            timestamp = datetime.now()
            text = "NO_MOTION"

            # convert frame to grayscale, and blur it
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
            thresh = cv2.threshold(frame_delta, 5, 255,
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
                        self.min_save_seconds:
                    # increment the motion counter
                    self.motionCounter += 1

                    # check to see if the number of frames with consistent
                    # motion is high enough
                    if self.motionCounter >= self.min_motion_frames:
                        # write the image to disk
                        pic_path = self.make_picture_path(datetime.now())
                        cv2.imwrite(pic_path, frame)

                        # send MMS and record some video
                        print("\nMotion detected!!! Sending MMS, and recording a 10 "
                              "sec clip")
                        self.send_mms(pic_path)
                        self.take_video(10)

                        # update the last uploaded timestamp and reset the
                        # motion counter
                        self.lastSaved = timestamp
                        self.motionCounter = 0
                        time.sleep(self.min_save_seconds)

            # otherwise, the room is not MOTION
            else:
                self.motionCounter = 0

            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)

    def take_video(self, duration):
        vid_path = '{}.h264'.format(datetime.now())
        self.camera.start_recording(vid_path)
        time.sleep(duration)
        self.camera.stop_recording()
        print("\nWrote {} to disk.".format(vid_path))

    def send_mms(self, picture_path):
        print("\nSending MMS message")
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
        return '{}.jpg'.format(timestamp)


cam = py_sPi(30, (1920, 1080))

cam.detect_motion()
