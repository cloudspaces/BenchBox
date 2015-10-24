#!/bin/bash


echo "Install Zero RPC dependencies"


# gevent for testing purpose
# curl -O https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.tar.gz && tar xvzpf gevent-1.0rc2.tar.gz && cd gevent-1.0rc2 && sudo python setup.py install

# Simple script for installing ZeroRPC on Ubuntu 12.04 LTS

# System dependencies

# First install ZeroMQ
sudo apt-get -y install libzmq-dev

# Next install libevent, an event notification library required by zerorpc
sudo apt-get -y install libevent

# Python dependencies

# Now install pyzmq: Python bindings for ZeroMQ
# If you don't already have pip installed:
sudo apt-get -y install python-setuptools
sudo apt-get -y install python-pip
sudo pip install pyzmq

# Now we can install ZeroRPC
sudo pip install zerorpc

# Node.js dependencies

# Just install the ZeroRPC node module
sudo npm install -g node-gyp
sudo npm install -g zerorpc