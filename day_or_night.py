import json
import sys
from urllib import urlopen
from dateutil import tz
from datetime import datetime, timedelta


def day_or_night_check():
	# Lat, Long tuple for Lewiston, ME
	gps_coords = (44.089594, -70.172185)

	api_url='http://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0'.format(
		gps_coords[0], gps_coords[1])

	from_zone=tz.tzutc()
	to_zone=tz.tzlocal()

	response=json.loads(
		urlopen(api_url).read()
		)
	sys.stdout.write("\n sunrise-sunset api response: {}".format(response['status']))

	if response["status"] == "OK":
		times=response["results"]

		sunrise=times["sunrise"].split("+")[0]
		sunrise=datetime.strptime(sunrise, '%Y-%m-%dT%H:%M:%S') - timedelta(hours=4)

		sunset=times["sunset"].split("+")[0]
		sunset=datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S') - timedelta(hours=4)

		now=datetime.now()

		if now >= sunrise and now <= sunset:
			return "DAY_PI"
		elif now < sunrise and now > sunset:
			return "NIGHT_PI"

	else:
		return "ERROR"
