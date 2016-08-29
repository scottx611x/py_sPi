#!usr/bin/bash

# sudo dpkg-reconfigure dash -> select NO!

sudo killall python
sudo rm -rf nohup.out
mkdir -p vids
mkdir -p pics

#pip install virtualenvwrapper==4.7.0

#export PATH=/usr/local/bin:$PATH
#source /usr/local/bin/virtualenvwrapper.sh

#mkvirtualenv py_sPi
#workon py_sPi
pip install -r requirements.txt
sudo nohup python flask_server.py &
sleep 5
nohup python py_sPi.py &
sudo tail -f nohup.out

