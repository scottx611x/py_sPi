#-*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com

# --------------------------------------
import httplib2
import os
import cv2
import dropbox
import sys
import ephem
import threading
from sys import stdout
import time
import json
import uuid
from datetime import datetime, timedelta
from twilio.rest import TwilioRestClient
from dropbox.exceptions import ApiError
from picamera.array import PiRGBArray
from picamera import PiCamera


global RETRY_TWILIO_SEND
RETRY_TWILIO_SEND = 0

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)
    sys.exit()


def day_or_night_pi():
    sunlight = ephem.Sun()
    city = ephem.city('Boston')
    sunlight.compute(city)
    twilight = -12 * ephem.degree
    if sunlight.alt > twilight:
        return "DAY_PI"
    else:
        return "NIGHT_PI"


def run_in_thread(fn):
    """
    :param fn: function to be run in its own thread
    :return: thread object
    """
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run

class py_sPi(object):
    """
        Class that allows one to instantiate a stream that will detect
        motion using a raspberry pi and V2 Cam.
    """

    camera = PiCamera()
    account = settings["TWILIO_ACCOUNT"]
    token = settings["TWILIO_TOKEN"]

    client = TwilioRestClient(account, token)
    dbx = dropbox.Dropbox(settings["DROPBOX_ACCESS_TOKEN"])

    def __init__(self, framerate, resolution, pi_type):
        self.start_time = datetime.now()

        self.pi_type = pi_type

        stdout.write("Camera initializing")

        self.camera.framerate = framerate
        self.camera.resolution = resolution

        stdout.write("Starting raw capture")

        self.raw_capture = PiRGBArray(self.camera, size=resolution)

        # Wait for the automatic gain control to settle
        time.sleep(5)

        # The weighted average to be calculated between frames (for use in
        # detecting change between frames)
        self.weighted_average = None

        # Amount of time to wait between sending messages
        self.send_interval = 5

        # Minimum amount of consecutive frames to allow motion in before
        # sending a message
        self.min_motion_frames = 3

        # Percent difference between "motion frame" and the averaged background
        # model (if you're experiencing lots of false positives increase
        # this!!!)
        self.delta_threshold = 19

        # Minimum area in frame that motion needs to happen within for a
        # message to be sent (total frame area is just your resolution
        # i.e. 1920 x 1080 = 2,073,600)
        self.min_area = (resolution[0] * resolution[1]) * .05

        self.video_duration = 10
        self.last_saved = datetime.now()
        self.motion_counter = 0

        stdout.write("Camera initialized")

    def detect_motion(self):
        stdout.write("Detecting Motion")

        self.last_checked_time = self.start_time

        # capture consecutive frames from the camera
        for frames in self.camera.capture_continuous(
                self.raw_capture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and MOTION/NO_MOTION text

            # Flush stdout every loop
            stdout.flush()

            frame = frames.array
            timestamp = datetime.now()
            text = "NO_MOTION"

            if self.last_checked_time <= timestamp - timedelta(minutes=45):
                stdout.write("Timestamp: {}".format(timestamp))

                self.last_checked_time = timestamp

                # Check if its the right time of day to run our type of Pi
                # We'll sleep for an hour and check again
                day_or_night = day_or_night_pi()
                if day_or_night != self.pi_type:
                    stdout.write("Not the right time to run our {}".format(
                        self.pi_type))
                    stdout.write("day_or_night_check returned: {}".format(
                        day_or_night))
                    time.sleep(3600)
                else:
                    stdout.write("It's the right time to run our {}".format(
                        self.pi_type))
                    stdout.write("day_or_night_check returned: {}".format(
                        day_or_night))

            # convert frame to grayscale, and blur it
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the "average" frame is None, initialize it
            if self.weighted_average is None:
                self.weighted_average = gray.copy().astype("float")
                self.raw_capture.truncate(0)
                continue

            # accumulate the weighted average between the current frame and
            # previous frames, then compute the difference between the current
            # frame and running average
            cv2.accumulateWeighted(gray, self.weighted_average, 0.5)
            frame_delta = cv2.absdiff(
                gray, cv2.convertScaleAbs(self.weighted_average))

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

                # check to see if enough time has passed between message sends
                if (timestamp - self.last_saved).seconds >= \
                        self.send_interval:

                    # increment the motion counter
                    self.motion_counter += 1

                    # check to see if the number of frames with consistent
                    # motion is high enough
                    if self.motion_counter >= self.min_motion_frames:
                        # write the image to disk
                        pic_path = self.make_picture_path()
                        cv2.imwrite(pic_path, frame)
                        self.dropbox_upload(pic_path)

                        stdout.write("Motion detected!!! Recording a {} "
                                     "second "
                                     "clip".format(self.video_duration))
                        self.take_video(self.video_duration)

                        # update the last uploaded timestamp and reset the
                        # motion counter
                        self.last_saved = timestamp
                        self.motion_counter = 0

            # otherwise, the room is not MOTION
            else:
                self.motion_counter = 0

            # clear the stream in preparation for the next frame
            self.raw_capture.truncate(0)

    @run_in_thread
    def take_video(self, duration):
        """
            Takes a raw .h264 video and converts to .mp4

            param: duration: an int representing the length of video to be
            taken

            returns: the relative path to said video or None if something fails
            during mp4 conversion
        """
        stdout.write("Taking Video")

        vid_path = 'vids/{}.h264'.format(uuid.uuid4()).replace("-", "")
        self.camera.start_recording(vid_path)
        time.sleep(duration)
        self.camera.stop_recording()
        stdout.write("Wrote {} to disk.".format(vid_path))

        new_vid_path = vid_path.replace("h264", "mp4")

        try:
            os.system("MP4Box -add {} {}".format(vid_path, new_vid_path))
            os.remove(vid_path)
            self.dropbox_upload(new_vid_path)
        except Exception as e:
            stdout.write("MP4 Converison Error {}".format(e))
            return None

    def make_picture_path(self):
        """
            Return a unique path for jpgs so we can ensure we're fetching
            only one file in our Flask calls
        """
        return 'pics/{}.jpg'.format(uuid.uuid4()).replace("-", "")

    @run_in_thread
    def dropbox_upload(self, path):
        """
        :param path: Full filesystem path of file to be uploaded
        :return: Publicly shared dropbox link to uploaded file
        """
        with open(path, 'rb') as f:
            data = f.read()
            try:
                self.dbx.files_upload(data, "/" + path)
                response = self.dbx.sharing_create_shared_link_with_settings(
                    "/" + path)
                os.remove(path)
            except ApiError as e:
                stdout.write(e)
            else:
                # send mms using url of succesfully uploaded file
                self.send_mms(response.url)

    @run_in_thread
    def send_mms(self, dropbox_url):
        """
            Takes a relative path to a picture and video and attempts to
            send MMS messages that include a download link to said video
            to a preset list of recipients
            param: dropbox_url: url to file in dropbox account
        """
        global RETRY_TWILIO_SEND
        stdout.write("\nSending MMS message")

        body = "Motion detected!"
        numbers = ["+12075136000"]
        recipient_states = {item: None for item in numbers}

        def twilio_send(recipients):
            """
                Recursive method to ensure that all message are
                properly sent to each recipient defined
                NOTE: I had to introduce this feature because twilio
                would raise httplib2.ServerNotFoundError-s periodically
                param: recipients: dict in the form of  {<phone_number>: <message_send_state>, ...}
                returns: the same recipients dict with updated <message_send_states>
            """
            global RETRY_TWILIO_SEND

            if RETRY_TWILIO_SEND > 5:
                stdout.write(
                    "\nCan't reach twilio :( Waiting for a minute then trying again")

                time.sleep(60)
                RETRY_TWILIO_SEND = 0

            for number in recipients:
                try:
                    self.client.messages.create(
                        to=number,
                        from_="+15106626969",
                        body=body,
                        media_url=[dropbox_url]
                    )
                    recipients[number] = "SUCCESS"

                except (httplib2.ServerNotFoundError, Exception):
                    recipients[number] = "FAILURE"

            return recipients

        recipients = twilio_send(recipient_states)

        while recipients:
            recipients_temp = {}

            for recipient in recipients:
                if recipients[recipient] == "FAILURE":
                    recipients_temp[
                        recipient] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

            recipients = twilio_send(recipients_temp)

        RETRY_TWILIO_SEND = 0

cam = py_sPi(30, (1920, 1080), settings["PI_TYPE"])
cam.detect_motion()
