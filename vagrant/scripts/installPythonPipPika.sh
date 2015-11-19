#!/bin/bash


sudo apt-get -y install python-dev


dpkg -l python-setuptools
if [ $? -ne 0 ]
then
sudo apt-get -y install python-setuptools
fi
dpkg -l python-pip
if [ $? -ne 0 ]
then
sudo apt-get -y install python-pip
fi

sudo pip install pika