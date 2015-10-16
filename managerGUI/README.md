# managerGUI



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