#!/bin/bash


echo 'Start the grafana server'
sudo service grafana-server start

echo 'Start rabbit-mq server'
sudo service rabbitmq-server restart


echo 'Start the zeroRPC server'
python zerorpc/startZeroRPC.py &

echo 'Start the nodeManager server'
npm start

echo 'Start/OK'