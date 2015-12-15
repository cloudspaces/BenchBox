#!/bin/bash


echo "Installing influxDB"
wget http://influxdb.s3.amazonaws.com/influxdb_0.9.5.1_amd64.deb
sudo dpkg -i influxdb_0.9.5.1_amd64.deb


# sudo service influxdb start # start it???