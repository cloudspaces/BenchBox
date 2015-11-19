#!/bin/bash



echo "Start RPC and RMQ"
nohop python startRabbitMQ.py
nohop python startZeroRPC.py
