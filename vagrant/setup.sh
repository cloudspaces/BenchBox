#!/bin/bash -x


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

if [ -f prod_status.pid ]
then
line=($(<"prod_status.pid"))
kill 0 $line
if [ $? -eq 0 ]
then
kill -9 $line
fi
fi
nohup python ./prod_status.py --msg setupFinished --topic `hostname` > /dev/null 2>&1 & echo $! > prod_status.pid
fi;

