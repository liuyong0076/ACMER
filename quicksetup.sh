#!/bin/bash
apt-get update
apt-get install gcc python3 python3-pip python3-dev mysql-server build-essential libssl-dev libffi-dev libxml2 libxml2-dev libxslt1-dev zlib1g-dev phantomjs libmysqlclient-dev 
apt-get install unzip libnss3-dev libxss1 xvfb
pip3 install django lxml django-crontab beautifulsoup4 requests markdown selenium phantomjs pygments mysqlclient -i https://mirrors.aliyun.com/pypi/simple/
wget http://dl.google.com/linux/deb/pool/main/g/google-chrome-stable/google-chrome-stable_70.0.3538.77-1_amd64.deb
wget http://npm.taobao.org/mirrors/chromedriver/70.0.3538.97/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver
sudo mv -f chromedriver /usr/local/share/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver
dpkg -i google-chrome-stable_70.0.3538.77-1_amd64.deb || apt-get -f install && dpkg -i google-chrome-stable_70.0.3538.77-1_amd64.deb
Xvfb :99 -ac -screen 0 1280x1024x24 &
export DISPLAY=:99