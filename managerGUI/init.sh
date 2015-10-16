#!/usr/bin/env bash



# init manager-rpc server
echo "start manager RPC Server"
python manager.py &



# init node server
echo "start manager GUI Server"
npm start