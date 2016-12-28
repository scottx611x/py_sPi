# -*- coding: utf-8 -*-
# Scott Ouellette | scottx611x@gmail.com
# --------------------------------------
import ephem
import threading


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