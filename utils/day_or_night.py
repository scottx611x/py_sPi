# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com

# --------------------------------------

import json
import sys
from urllib import urlopen
from datetime import datetime, timedelta

try:
    with open("config.json", 'r') as f:
        settings = json.load(f)
except IOError as e:
    error_msg = "Could not open '{}': {}".format("config.json", e)


def day_or_night_check():
    # Lat, Long tuple for Lewiston, ME
    gps_coords = (settings.COORDS.LAT, settings.COORDS.LONG)

    api_url = \
        'http://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0'.format(
            gps_coords[0], gps_coords[1])

    response = json.loads(
        urlopen(api_url).read()
    )
    sys.stdout.write(
        "\n sunrise-sunset api response: {}".format(response['status']))

    if response["status"] == "OK":
        times = response["results"]

        sunrise = times["sunrise"].split("+")[0]
        sunrise = datetime.strptime(sunrise, '%Y-%m-%dT%H:%M:%S') - timedelta(
            hours=4)

        sunset = times["sunset"].split("+")[0]
        sunset = datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S') - timedelta(
            hours=4)

        now = datetime.now()
        sys.stdout.write(
            "Now: {}, Sunset: {}, Sunrise: {}".format(now, sunset, sunrise))
        sys.stdout.flush()

        if sunrise <= now <= sunset:
            return "DAY_PI"
        elif sunrise > now > sunset:
            return "NIGHT_PI"

    else:
        return "ERROR"
