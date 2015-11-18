#!/bin/bash -x


echo "Install Zero RPC dependencies"


# gevent for testing purpose
# curl -O https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.tar.gz && tar xvzpf gevent-1.0rc2.tar.gz && cd gevent-1.0rc2 && sudo python setup.py install

# Simple script for installing ZeroRPC on Ubuntu 12.04 LTS

# System dependencies

# First install ZeroMQ
sudo apt-get -y install libpq-dev
sudo apt-get -y install python-dev
sudo apt-get -y install libzmq-dev

# Next install libevent, an event notification library required by zerorpc
dpkg -l libevent
if [ $? -ne 0 ]
then
# wget http://monkey.org/~provos/libevent-1.4.13-stable.tar.gz
sudo apt-get -y install libevent-dev
fi
# Python dependencies

# Now install pyzmq: Python bindings for ZeroMQ
# If you don't already have pip installed:
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
sudo pip install pyzmq
sudo pip install python-nmap
# Now we can install ZeroRPC
sudo pip install zerorpc


# Node.js dependencies

# Just install the ZeroRPC node module
npm list -g node-gyp
if [ $? -ne 0 ]
then
sudo npm update -g node-gyp
fi
npm list -g zerorpc
if [ $? -eq 1 ]
then
sudo npm install -g zerorpc
fi
if [ $? -ne 0 ]
then
sudo npm update -g zerorpc
fi
