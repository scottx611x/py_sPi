import sys
import json
import unittest
from py_sPi import py_sPi

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)
    sys.exit()


class PySpiTests(unittest.TestCase):
    def setUp(self):
        self.pi_camera = py_sPi(30, (1920, 1080), settings.PI_TYPE)

    def tearDown(self):
        pass

    def test_make_picture_path(self):
        self.assertRegexpMatches(
            self.pi_camera.make_picture_path(),
            '[0-9a-f]{32}'
        )
