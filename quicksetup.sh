#!/bin/bash
apt-get update
apt-get install gcc python3 python3-pip python3-dev mysql-server build-essential libssl-dev libffi-dev libxml2 libxml2-dev libxslt1-dev zlib1g-dev phantomjs libmysqlclient-dev
pip3 install django lxml django-crontab beautifulsoup4 requests markdown selenium phantomjs pygments mysqlclient -i https://mirrors.aliyun.com/pypi/simple/