#!/bin/bash -x



pgrep -f prod_status.py | xargs kill -9

echo "#4 Start prod_status"
nohup python prod_status.py --msg setupFinished --topic `hostname`
echo $! > /tmp/prod_status.pid
