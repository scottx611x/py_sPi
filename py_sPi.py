import sys
import time
from datetime import datetime
from fractions import Fraction
from picamera import PiCamera

camera = PiCamera()


class py_sPi(object):

    def __init__(self, day_or_night, resolution):
        self.camera_type = day_or_night
        self.picture_paths = []
        self.video_paths = []

        sys.stdout.write(
            "\nInitializing {} camera...".format(self.camera_type))

        camera.resolution = resolution
        # Set a framerate of 1/6fps, then set shutter
        # speed to 6s and ISO to 800
        camera.framerate = Fraction(1, 6)
        camera.shutter_speed = 6000000
        camera.exposure_mode = 'off'
        camera.iso = 800
        # Give the camera a good long time to measure AWB
        # (you may wish to use fixed AWB instead)
        time.sleep(10)
        sys.stdout.write("\nCamera initialized")

    def take_picture(self, pictures_to_take):
        while pictures_to_take:
            time.sleep(3)
            pic_path = '{}.png'.format(datetime.now())
            camera.capture(pic_path)
            self.picture_paths += [pic_path]
            pictures_to_take -= 1
            sys.stdout.write("\nWrote {} to disk.".format(pic_path))

    def take_video(self, duration):
        vid_path = '{}.h264'.format(datetime.now())
        camera.start_recording(vid_path)
        time.sleep(duration)
        camera.stop_recording()
        sys.stdout.write("\nWrote {} to disk.".format(vid_path))


day_cam = py_sPi("day", (1920, 1068))
day_cam.take_picture(1)
