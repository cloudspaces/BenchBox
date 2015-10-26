#!/bin/bash -ex

required_node_version="v0.12.7"

echo "Check if curl is installed"
which curl
if [ ! $? -eq 0 ]
	then
	echo "Installing Curl"
	sudo apt-get install curl
else
	echo "Curl already installed"
fi




echo "Check if node is installed"
which nodejs
if [ ! $? -eq 0 ]
	then

		# curl --silent --location https://deb.nodesource.com/setup_0.12 | bash -
		# apt-get install --yes nodejs

		echo "Check if node is installed"
		curl -sL https://deb.nodesource.com/setup_0.12 | sudo bash -
		sudo apt-get install -y nodejs

		echo  "Finish installing nodejs"
else
	echo "Node is already installed"
	node_version=$(node -v)
	if [ $node_version == $required_node_version ]
	then
	echo OK
	else
	echo FaIL
		echo "install node 0.12.7"
		curl -sL https://deb.nodesource.com/setup_0.12 | sudo bash -
		sudo apt-get install -y nodejs
	fi
fi