#!/usr/bin/env bash -ex




./installZeroRPC.sh
./installNodejs.sh
./installGraphite.sh up &
./installMongoBD.sh &


# init manager-rpc server
echo "start manager RPC Server"
python static/manager.py &

# init node server
echo "start manager GUI Server"
npm start

