sudo killall python
sudo rm -rf nohup.out
mkdir -p vids
mkdir -p pics
pip install virtualenvwrapper==4.7.0
source "/usr/bin/virtualenvwrapper.sh"
export WORKON_HOME="/opt/virtual_env/"
mkvirtualenv py_sPi
workon py_sPi
pip install -r requirements.txt
#sudo nohup python -m SimpleHTTPServer 7777 &
sudo nohup python flask_server.py
sleep 5
nohup python py_sPi.py &
sudo tail -f nohup

