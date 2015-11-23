#!/bin/bash -x

if [ -f prod_status.pid ]
    then
    line=($(<"prod_status.pid"))
    kill -9 $line
fi
echo "#4 Start prod_status"
python prod_status.py --msg setupFinished --topic `hostname`
echo $! > prod_status.pid
