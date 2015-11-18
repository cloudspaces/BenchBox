#!/bin/bash



echo "Start RPC and RMQ"
python startRMQ.py &
python startRPC.py &
