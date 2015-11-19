#!/bin/bash


sudo apt-get -y install python-dev

dpkg -l python-pip
if [ $? -ne 0 ]
then
sudo apt-get -y install python-pip
fi
dpkg -l python-setuptools
if [ $? -ne 0 ]
then
sudo apt-get -y install python-setuptools
fi

sudo pip install pika