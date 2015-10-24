#!/usr/bin/env bash




./installZeroRPC.sh
./installNodejs.sh
./installGraphite.sh up &
./installMongoBD.sh &


# init manager-rpc server
echo "start manager RPC Server"
python manager.py &

# init node server
echo "start manager GUI Server"
npm start

