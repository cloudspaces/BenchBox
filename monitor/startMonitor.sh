#!/bin/bash -x


echo 'kill socketListener.sh'
killer_pid=$(pidof python)
if [ $? -ne 0 ]
then
echo 'No such pid'
else
echo 'vagrant' | sudo -S kill -9 $killer_pid
fi
echo 'start socketListener';
if [ -d ~/monitor ]; then  
cd ~/monitor/py_cpu_monitor
echo 'vagrant' | sudo -S python SocketListener.py;
echo 'stacksync client and monitor started';  
else  
echo 'stacksync client monitoring not available';  
fi
