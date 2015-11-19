#!/usr/bin/env bash

#
# Add Vagrant Box
#

echo "Inicializar instalación de dependencias en los Hosts"

if [ -f ./debian-7.0-amd64.box ]; then
	echo 'box/OK';
	ls *.box
else
	echo 'no..., check if other path';
	wget https://www.dropbox.com/s/sdupbseays0f7ik/debian-7.0-amd64.box;
fi


# check if the machine has installed python dependecy libraries
# instalar owncloud i stacksync client
# https://github.com/stacksync/desktop/releases/download/v2.0-alpha2/stacksync_2.0_all.deb


echo "Instalation fin"


echo "now Vagrant ready to Start! --> vagrant up"