#!/bin/bash -x



pgrep -f prod_status.py | xargs kill -9
echo "-----------------"
echo "Start prod_status"
echo "-----------------"

nohup python prod_status.py --msg provisionOK --topic `hostname`
echo $! > /tmp/prod_status.pid
