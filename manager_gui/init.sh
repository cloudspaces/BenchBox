#!/usr/bin/env bash




./installNodejs.sh
./installZeroRPC.sh
# ./installGraphite.sh
# ./installMongoBD.sh


# init manager-rpc server
echo "start manager RPC Server"
python manager.py &



# init node server
echo "start manager GUI Server"

npm start