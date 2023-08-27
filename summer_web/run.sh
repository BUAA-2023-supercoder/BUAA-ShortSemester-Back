#!/bin/bash

killall -9 uwsgi
rm uwsgi.log
uwsgi --ini uwsgi.ini

ps -ef | grep uwsgi

sudo service nginx reload
sudo service nginx start
echo "successful"