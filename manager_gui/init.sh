#!/bin/bash -ex




./installZeroRPC.sh
./installNodejs.sh
./installGraphite.sh up &
./installMongoBD.sh &


# init manager-rpc server
echo "start manager RPC Server"
python static/manager.py &

# init node server
echo "start manager GUI Server"
npm install # install the package to node_modules defined at the package.json
npm start

