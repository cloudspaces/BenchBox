#!/bin/bash

if [ -f prod_status.pid ]
    then
    line=($(<"prod_status.pid"))
    kill 0 $line
    if [ $? -eq 0 ]
        then
        kill -9 $line
    fi
fi
echo "#4 Start prod_status"
nohup python ./prod_status.py --msg setupFinished --topic `hostname` > /dev/null 2>&1 & echo $! > prod_status.pid

