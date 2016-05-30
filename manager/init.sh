#!/bin/bash -ex






installers/installVagrantVBox.sh
installers/installZeroRPC.sh
installers/installRabbitMQ.sh
installers/installUserRabbitMQ.sh
installers/installNodejs.sh

# installers/installGraphite.sh up &
installers/installInfluxDB.sh
installers/installGraphana.sh
installers/installMongoBD.sh &

# init manager-rpc server
echo "start manager RPC Server"
nohup python zerorpc/startZeroRPC.py &> nohup_zerorpc.out&

# init node server
echo "start manager GUI Server"
npm install # install the package to node_modules defined at the package.json
npm start &> nohup_manager.out&

