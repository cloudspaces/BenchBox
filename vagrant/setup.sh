#!/bin/bash


print "Setup Dummy Host"


# pwd will be:  ~/BenchBox 

if [ -d scripts ]; then

echo "#0 InstallVagrant and VirtualBox" 
sudo ./scripts/installVagrantVBox.sh;


echo "#1 Download Vagrant Box Image"
sudo ./scripts/installDependencies.sh;


echo "#2 AssignCredentialsToProfile"
./scripts/config.owncloud.sh;
./scripts/config.stacksync.sh;  # '%s' # h['stacksync-ip']

echo "#3 Install RabbitMQ Pip Pika"
sudo ./scripts/installPythonPipPika.sh


python vagrant/emit_status.py --msg setupFinished;


fi;

END