#!/bin/bash


print "Setup Dummy Host"
: <<'END'

# pwd will be:  ~/BenchBox 

if [ -d vagrant/scripts ]; then 

echo "#0 InstallVagrant and VirtualBox" 
sudo vagrant/scripts/installVagrantVBox.sh;   


echo "#1 Download Vagrant Box Image"
sudo vagrant/scripts/installDependencies.sh;  


echo "#2 AssignCredentialsToProfile"
vagrant/scripts/config.owncloud.sh;
vagrant/scripts/config.stacksync.sh;  '%s' # h['stacksync-ip'] 

python vagrant/emit_status.py --msg setupFinished;


fi;

END