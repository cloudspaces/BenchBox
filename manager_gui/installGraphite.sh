#!/bin/bash -ex

echo "Start synthesize"
cd graphite
# sudo ./install

action=$1
#vagrant plugin list | grep vagrant-vbguest
#plugin_status=$?
#if [ $plugin_status -ne 0 ]
#then
vagrant plugin update vagrant-vbguest
#fi

case "$action" in
("up") echo "start graphite"
vagrant up
;;
("halt") echo "wait graphite"
vagrant halt
;;
("destroy") echo "remove graphite"
vagrant destroy
;;
(*) echo "default show status"
vagrant status
;;
esac
# vagrant up

