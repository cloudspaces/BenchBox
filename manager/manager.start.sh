#!/bin/bash


echo 'Start the grafana server'
sudo service grafana-server start

echo 'Start rabbit-mq server'
sudo service rabbitmq-server start

echo 'Stop mongodb server'
sudo service mongodb start

echo 'Stop influx-db server'
sudo service influxdb start

echo 'Start the zeroRPC server'
if [ "`hostname`" = "manager" ]
then
echo "Change to vagrant directory"
cd /vagrant
else
echo "No change"
fi



echo `pwd`

line=$(ps aux | grep -v grep |  grep zerorpc | awk '{print $2}')
if [ -z "$line" ]
    then
    echo "No results"
    else
    echo "Have result"
    kill -9 $line
fi

python zerorpc/startZeroRPC.py &
echo 'Start the nodeManager server'

echo "Wait the servers to start"
sleep 10

if [ `whoami` = "root" ]
then
echo "Manager launch from vagrant"
if [ -d "/vagrant/node_modules" ];
then
    echo "Node_modules already exists"
    # noop
    npm rebuild --no-bin-links
else
    echo "Node_modules dont exist"
    mv /home/vagrant/node_modules /vagrant
fi
else
echo "Manager launch from local"
echo `whoami`
fi
npm start

echo 'Start/OK'
