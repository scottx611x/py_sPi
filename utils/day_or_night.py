# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com

# --------------------------------------
import ephem


def day_or_night_pi():
    sunlight = ephem.Sun()
    city = ephem.city('Boston')
    sunlight.compute(city)
    twilight = -12 * ephem.degree
    if sunlight.alt > twilight:
        return "DAY_PI"
    else:
        return "NIGHT_PI"
