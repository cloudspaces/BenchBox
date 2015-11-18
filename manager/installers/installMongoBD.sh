#!/bin/bash -x

echo 'Install MongoDB'
sudo apt-get  -y install mongodb

#echo 'Start MongoDB'
#sudo /etc/init.d/mongodb start


which mongod
if [ ! $? -eq 0 ]
	then


		echo "Mongo not installed"

		echo "Import the public key used by the package management system"
		sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10

		echo "Create a /etc/apt/sources.list.d/mongodb-org-3.0.list file for MongoDB"
		echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list


		echo "Reload local package database."
		sudo apt-get update

		echo "Install the MongoDB packages. - install latest stable version"
		# sudo apt-get install -y mongodb-org
		sudo apt-get install -y mongodb-org=3.0.7 mongodb-org-server=3.0.7 mongodb-org-shell=3.0.7 mongodb-org-mongos=3.0.7 mongodb-org-tools=3.0.7



		echo "mongodb-org hold" | sudo dpkg --set-selections
		echo "mongodb-org-server hold" | sudo dpkg --set-selections
		echo "mongodb-org-shell hold" | sudo dpkg --set-selections
		echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
		echo "mongodb-org-tools hold" | sudo dpkg --set-selections


		echo "Mongo installed"
else
	sudo service mongodb status
	sudo service mongodb start

	if [ $? -eq 0 ]
	then
		exit 0
	else
		exit 1
		#sudo service mongod start
	fi

fi


