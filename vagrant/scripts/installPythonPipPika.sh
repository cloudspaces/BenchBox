#!/bin/bash


dpkg-query -W python-dev
if [ $? -ne 0 ]
then
sudo apt-get -y install python-dev
fi
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

python -c "import pika"

if [ $? -ne 0 ]
then
sudo pip install pika
fi