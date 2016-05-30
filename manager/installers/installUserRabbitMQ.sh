#!/bin/bash


if [ "$#" -eq 1 ]; then
    USER_NAME=$1
    echo "Username defined [TRUE]: use default: $1"
else
    echo "Username defined [FALSE]: use default: benchbox"
    USER_NAME='benchbox'
    echo "Add rabbitmq user"
fi


sudo rabbitmqctl list_users | grep -w "^$USER_NAME"
if [ $? -eq 0 ]
then
echo "User already exists"
else
echo "RabbitUser: $USER_NAME"
sudo rabbitmqctl add_user $USER_NAME $USER_NAME
sudo rabbitmqctl set_user_tags $USER_NAME $USER_NAME
sudo rabbitmqctl set_permissions -p / $USER_NAME ".*" ".*" ".*"
fi
