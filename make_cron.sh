# Write our current crontab to file
crontab -l > coffee_is_tasty

# Check if it's empty or not
if [ -s coffee_is_tasty ]
then
	# crontab isn't empty so let's not write over it
        echo "crontab is already populated!"
else
	# echo new cronjobs into file

        # These jobs below will remove files older than one week in our pics & vids directories
        echo "0 2 * * 0 find ~/Code/python/py_sPi/pics/*.jpg -mtime +7 -exec rm {} \;" >> coffee_is_tasty
        echo "0 2 * * 0 find ~/Code/python/py_sPi/vids/*.mp4 -mtime +7 -exec rm {} \;" >> coffee_is_tasty
        echo "0 2 * * 0 find ~/Code/python/py_sPi/vids/*.h264 -mtime +7 -exec rm {} \;" >> coffee_is_tasty
	# install new cron file
        crontab coffee_is_tasty
fi

rm coffee_is_tasty
