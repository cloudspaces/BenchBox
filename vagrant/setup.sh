#!/bin/bash


echo "Setup Dummy Host"


# pwd will be:  ~/BenchBox

if [ -d scripts ]; then

echo "#0 InstallVagrant and VirtualBox"
sudo ./scripts/installVagrantVBox.sh >/dev/null;


echo "#1 Download Vagrant Box Image"
sudo ./scripts/installDependencies.sh >/dev/null;


echo "#2 AssignCredentialsToProfile"
sudo ./scripts/config.owncloud.sh >/dev/null;
sudo ./scripts/config.stacksync.sh >/dev/null;  # '%s' # h['stacksync-ip']
sudo ./scripts/config.megasync.sh `hostname` >/dev/null;



echo "#3 Install RabbitMQ Pip Pika"
sudo ./scripts/installPythonPipPika.sh >/dev/null;


fi;

