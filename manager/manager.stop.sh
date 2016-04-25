#!/bin/bash


echo 'Stop the grafana server'
sudo service grafana-server stop

echo 'Stop rabbit-mq server'
sudo service rabbitmq-server stop


echo 'Stop the zeroRPC server'
# python zerorpc/startZeroRPC.py &
line=$(ps aux | grep -v grep |  grep zerorpc | awk '{print $2}')
if [ -z "$line" ]
    then
    echo "No results"
    else
    echo "Have result"
    kill -9 $line
fi


echo 'Start the nodeManager server'
line=$(ps aux | grep -v grep |  grep ./bin/www | awk '{print $2}')
if [ -z "$line" ]
    then
    echo "No results"
    else
    echo "Have result"
    kill -9 $line
fi

echo 'Start/OK'