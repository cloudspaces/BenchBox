#!/bin/bash -ex



echo "Installing python dependent RabbitMQ server with Pika Library"
# https://www.rabbitmq.com/install-debian.html


echo "Install recent version of Erlang"

# required also erlang =>
sudo apt-get install -y erlang  erlang-nox  erlang-manpages erlang-doc


echo "Download the"

wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.5.6/rabbitmq-server_3.5.6-1_all.deb

sudo dpkg -i rabbitmq-server_3.5.6-1_all.deb
if [ $? -ne 0 ]
then
echo "Fail"
else
echo "OK"
fi


# ''' installing a local rabbitmq should be optional '''
# sudo apt-get install rabbitmq-server
sudo pip install termcolor
sudo pip install pika

