# managerGUI


# prerequisite:

have the following ports free:
* config.vm.network "forwarded_port", guest: 8888, host: 8888 # manager web interface
* config.vm.network "forwarded_port", guest: 5672, host: 5672 # rabbitmq
* config.vm.network "forwarded_port", guest: 15672, host: 15672 # webinterface rabbitmq
* config.vm.network "forwarded_port", guest: 3000, host: 3000 # grafana server
* config.vm.network "forwarded_port", guest: listens in port 8083 (web) and 8086 (HTTP API).
# depencies:

* nodejs 4.3.4


# info

rabbitmq management:
http://localhost:15672/#/
* user: test
* pass: test


# issue at installing
## nodejs npm dependency:
	* sudo add-apt-repository ppa:chris-lea/zeromq
    * sudo add-apt-repository ppa:chris-lea/libpgm
    * sudo apt-get update
    * sudo apt-get install libzmq3-dev


# nodejs-client
## powered with:
	* angularjs (single page app)... [ref]: https://docs.angularjs.org/tutorial/step_05
	* express
	* zerorpc [ref]: http://pycon-2012-notes.readthedocs.org/en/latest/dotcloud_zerorpc.html
	* mongodb, session storage [ref]: https://docs.mongodb.org/getting-started/node/client/3


# todos

LocalStorage: data persistent even on closure of the web browser
SessionStorage: pre tab closure

# MEAN Stack

CRUD = Create-Read-Update-Delete

# auto nodeserver refresh :
	sudo npm install -g supervisor
	run supervisor ./bin/www


# instalar graphite log server
	https://github.com/obfuscurity/synthesize
	* at the mamanger machine, as a virtual machine or a deamon.