#!/bin/bash

# Most Rpi's don't have bash, but have "dash"
# sudo dpkg-reconfigure dash -> select NO if necessary

sudo killall python

# Remove old nohup log
sudo rm -rf nohup.out

# Make our dirs for pics and vids if need be
mkdir -p vids
mkdir -p pics

# Install requirements
pip install -r requirements.txt --quiet

# Run our py_sPi script
nohup python py_sPi.py &

# Peep the output
sudo tail -f nohup.out

