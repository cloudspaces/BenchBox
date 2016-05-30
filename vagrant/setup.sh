#!/bin/bash -x


print "Setup Dummy Host"


# pwd will be:  ~/BenchBox

if [ -d scripts ]; then

echo "#0 InstallVagrant and VirtualBox"
sudo ./scripts/installVagrantVBox.sh;


echo "#1 Download Vagrant Box Image"
sudo ./scripts/installDependencies.sh;


echo "#2 AssignCredentialsToProfile"
sudo ./scripts/config.owncloud.sh;
sudo ./scripts/config.stacksync.sh;  # '%s' # h['stacksync-ip']
sudo ./scripts/config.megasync.sh `hostname`;



echo "#3 Install RabbitMQ Pip Pika"
sudo ./scripts/installPythonPipPika.sh;


fi;

