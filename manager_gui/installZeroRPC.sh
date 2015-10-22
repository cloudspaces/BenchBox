#!/bin/bash


echo "Install Zero RPC dependencies"


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
sudo pip -y install pyzmq

# Now we can install ZeroRPC
sudo pip -y install zerorpc

# Node.js dependencies

# Just install the ZeroRPC node module
sudo npm install -g zerorpc