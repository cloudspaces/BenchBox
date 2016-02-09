console.log("init.js");

bugall = null
angular.module('app', ['ngRoute', 'ngResource'])

    //---------------
    // Services
    //---------------
    .directive('img-stream', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.bind('load', function () {
                    console.log("Image is loaded");
                });
            }
        };
    })

    //---------------
    // Factory
    //---------------

    .factory('Hosts', ['$resource', function ($resource) {
        // quin api rest utilitzar???
        return $resource('/hosts/:id', null, {
            'update': {
                method: 'PUT'
            }
        });
    }])

    //---------------
    // Controllers
    //---------------

    // hostDetails.html
    .controller('HostDetailCtrl', ['$scope', '$routeParams', 'Hosts', '$location',
        function ($scope, $routeParams, Hosts, $location) {
            $scope.host = Hosts.get({id: $routeParams.id});

            $scope.update = function () {
                Hosts.update({id: $scope.host._id}, $scope.host, function () {
                    $location.url('/');
                });
            };
            $scope.remove = function () {
                Hosts.remove({id: $scope.host._id}, function () {
                    $location.url('/');
                });
            };
        }])

    // hosts.html
    .controller('HostController', ['$scope', '$interval', 'Hosts',
        function ($scope, $interval, Hosts) {
            // default test settings
            $scope.run = {
                testOps: 10,
                testItv: 1,
                testProfile: 'backupsample', // modificar aixo mitjançant select
                testFolder: 'stacksync_folder', // modificar aixo mitjançant detector segons testClient
                testClient: 'StackSync', // modificar aixo en format select
                testOperation: 'hello',
                testMonitor: 'hello'
            };

            // controller actions
            $scope.editing = []; //  variable
            $scope.checkedAll = false;
            // Invocar manager de hosts

            // initial load
            $scope.hosts = Hosts.query(); // llistat de tots els hosts

            $scope.itv_time = 10000;
            $interval(callAtInterval, $scope.itv_time);

            function callAtInterval() {
                Hosts.query(function (items) {
                    // console.log(items)
                    angular.forEach(items, function (item, idx, all) {
                        if ($scope.hosts[idx].status === item.status) {
                            // console.log(" [not changed]" + $scope.hosts[idx].status + " : "+ item.status )
                        } else {
                            var changeDummy = " [changed dummyhost] from:  " + $scope.hosts[idx].status + " to " + item.status;
                            console.log(changeDummy);
                            $.notify(changeDummy, 'info');
                            $scope.hosts[idx].status = item.status
                        }
                        if ($scope.hosts[idx].status_sandbox !== item.status_sandbox) {
                            var changeSandBox = " [changed sandbox] from:  " + $scope.hosts[idx].status_sandbox + " to " + item.status_sandbox;
                            console.log(changeSandBox);
                            $.notify(changeSandBox, 'info');
                            $scope.hosts[idx].status_sandbox = item.status_sandbox
                        }
                        if ($scope.hosts[idx].status_benchbox !== item.status_benchbox) {
                            var changeBenchBox = " [changed] benchbox from:  " + $scope.hosts[idx].status_benchbox + " to " + item.status_benchbox;
                            console.log(changeBenchBox);
                            $.notify(changeBenchBox, 'info');
                            $scope.hosts[idx].status_benchbox = item.status_benchbox
                        }

                    })
                });

            }


            $scope.saveHost = function () {
                console.log('SaveHosts');
                console.log($scope);
                var host = new Hosts({
                    hostname: $scope.newHostHostname,
                    ip: $scope.newHostIp,
                    logging: $scope.newHostLogging
                });
                host.$save(function () {
                    $scope.hosts.push(host);
                    $scope.newHostHostname = ''; // clear textbox
                    $scope.newHostIp = ''; // clear textbox
                    $scope.newHostLogging = ''; // clear textbox
                });
                console.log(host);
                console.log($scope.hosts);
            };

            $scope.save = function () {
                if (!$scope.newHost || $scope.newHost.length < 1) return;
                var host = new Hosts({name: $scope.newHost, completed: false});
                host.$save(function () {
                    $scope.hosts.push(host);
                    $scope.newHost = ''; // clear textbox
                });
            };
            $scope.update = function (index) {
                var host = $scope.hosts[index];
                Hosts.update({id: host._id}, host);
                $scope.editing[index] = false;
            };
            $scope.ping = function (index) {
                var host = $scope.hosts[index];
                console.log(host);
                testConnection(host.ip, 22); // port ssh
                /*
                 Hosts.update({id: host._id}, host);
                 $scope.editing[index] = false;
                 */
            };
            $scope.rpc = function (name, cmd, ss) {
                console.info(name, cmd, ss);
                // console.log($scope)
                if (ss == undefined) {
                    console.log("Not ss cmd")
                } else {
                    console.info("ss cmd!");
                    cmd = cmd + $("#ssRadio input[type='radio']:checked")[0].value + ss;
                    console.log(cmd)
                }
                $('.' + name).each(function () {
                    // console.log(this)
                    if ($(this).prop('checked')) {
                        var checkedId = this.value;
                        var host = $scope.hosts.filter(function (item) {
                            return item._id == checkedId
                        });
                        console.log("rpcHost" + cmd, this.name, checkedId, host[0]);
                        if (cmd === 'setup') {
                            rpcHost(host[0], cmd)
                        }
                    }
                })
            };

            $scope.rmq = function (name, cmd) {
                console.log(arguments);
                var hosts = Array.prototype.slice.call(arguments, 2); // 3r till n are the target hosts
                console.log(hosts);
                console.log($scope.run.testOperation);
                console.log($scope.run);

                // setup testFolder
                switch($scope.run.testClient){
                    case "StackSync":
                        $scope.run.testFolder = "stacksync_folder";
                        break;
                    case "Dropbox":
                        $scope.run.testFolder = "Dropbox";
                        break;
                    default:

                        console.log("UNHANDLED PERSONAL_CLOUD!!!");
                        return;
                        break;


                }

                if(cmd == 'execute'){
                    cmd = $scope.run.testOperation
                }

                // hardcoded queue multiplexing
                switch (cmd){
                    case 'executor':
                        // handle benchBox - execute
                        cmd = $scope.run.testOperation;
                        break;

                    case 'monitor':
                        // handle sandBox - monitor
                        cmd = $scope.run.testMonitor;
                        break;
                    default:
                        // cmd is cmd xD
                        break;
                }

                //
                hosts.forEach(function (targetHost) {
                    console.log(targetHost);

                    $('.' + name).each(function () {
                        // console.log(this)
                        if ($(this).prop('checked')) {
                            var checkedId = this.value;
                            var host = $scope.hosts.filter(function (item) {
                                return item._id == checkedId
                            });
                            console.log("rmqHost: " + cmd, this.name, checkedId, host[0]);
                            host[0].rmq_queue = targetHost.toLowerCase();
                            host[0].test_setup = $scope.run;
                            // console.log(host[0])
                            rmqHost(host[0], cmd)
                        }

                    })

                })


            };

            $scope.checkAll = function (name) {

                $scope.checkedAll = !$scope.checkedAll;
                // console.log($scope.checkedAll );
                $('.' + name).each(function () {
                    // console.log(this);
                    // (this).prop('checked', $scope.checkedAll);
                    if ($(this).prop('checked') !== $scope.checkedAll)
                        $(this).trigger('click');

                });
            };

            $scope.edit = function (index) {
                console.log(index);
                console.log($scope.editing);
                $scope.editing[index] = angular.copy($scope.hosts[index]);
            };
            $scope.cancel = function (index) {
                $scope.hosts[index] = angular.copy($scope.editing[index]);
                $scope.editing[index] = false;
            };
            $scope.remove = function (index) {
                var host = $scope.hosts[index];
                Hosts.remove({id: host._id}, function () {
                    $scope.hosts.splice(index, 1);
                });
            };
        }])
    //---------------
    // Routes
    //---------------
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', { // quan accedeixo al root de home es criden aquests controladors
                templateUrl: 'html/hosts.html',
                controller: 'HostController'
            })
            .when('/:id', { // si especifico amb un id es crida aquest
                templateUrl: 'html/hostDetails.html',
                controller: 'HostDetailCtrl'
            });
    }]);

console.log("Home Script loaded");

GLOBAL_VAR = null;
console.log("Btn controller");


testConnection = function (ip, port, cb) {
    console.log('PING ---->', ip, port);
    // if i dont need to use the failure  function they recommend me to use post or get
    console.log("Get list");
    $.ajax({
        url: 'http://localhost:'+location.port+'/rpc/nmap',
        contentType: "application/json; charset=utf-8",
        data: {data: ip + ' ' + port},
        dataType: 'json',
        type: 'GET',
        success: function (data) {
            console.log('pc, Result:');
            console.log(data);
            // console.log(JSON.parse(JSON.stringify(data)));
            console.log('...');
            if (JSON.parse(data.result)) {
                $.notify('Success! ping(' + ip + ':' + port + ')', 'success');
            } else {
                $.notify('Warning! ping(' + ip + ':' + port + ')', 'warn');
            }
            // $.notify('Hello','info');
        },
        error: function (err) {
            console.log(err);
            console.log('pc, Error ping(' + ip + ':' + port + ')', err);
            $.notify('Error! ' + err, 'error ');
        }
    });
};

// cmd should be an object
rmqHost = function (host, cmd, cb) {

    var args = {
        ip: host.ip,
        hostname: host.hostname,
        login: host.logging,
        profile: host.profile,
        cred_stacksync: host.cred_stacksync,
        cred_owncloud: host.cred_owncloud,
        cmd: cmd,
        target_queue: host.rmq_queue,
        test: host.test_setup
    };

    appendAllParams(args, 'bb-config');
    appendAllHosts(args, 'bb-hosts');
    console.log("ARGS::::::");
    console.log(args);
    $.ajax({
        url: 'http://localhost:'+location.port+'/rmq/emit',
        data: args,
        timeout: 6000000, // 6000s ::100min
        type: 'GET',
        success: function (data) {
            console.log(args);
            console.log("Success, rmq!");
            console.log(data);
            $.notify('Run rmq! ' + host.hostname + ' ' + cmd, 'info');
        },
        error: function (err) {
            console.log(err);
            console.log('rmq, Error ' + host + ' ' + cmd + ' ', err);
            $.notify('Error! ' + err, 'error');
        }
    });
    if (cb !== undefined)
        cb(args);
};
rpcHost = function (host, cmd, cb) {

    var args = {
        ip: host.ip,
        hostname: host.hostname,
        login: host.logging,
        profile: host.profile,
        cred_stacksync: host.cred_stacksync,
        cred_owncloud: host.cred_owncloud,
        cmd: cmd

    };
    appendAllParams(args, 'bb-config');
    appendAllHosts(args, 'bb-hosts');
    $.ajax({
        url: 'http://localhost:'+location.port+'/rpc/rpc',
        data: args,
        timeout: 6000000, // 6000s ::100min
        type: 'GET',
        success: function (data) {
            console.log("Success, run start!");
            console.log(data);
            $.notify('Run rpc! ' + host.hostname + ' ' + cmd, 'info');
        },
        error: function (err) {
            console.log(err);
            console.log('pc, Error ' + host + ' ' + cmd + ' ', err);
            $.notify('Error! ' + err, 'error');
        }
    });
    if (cb !== undefined)
        cb(args);
};

appendAllParams = function (target, className) {
    $('.' + className).each(function () {
        // console.log(this)

        target[$(this).attr("id")] = (this.value);
    });
};

appendAllHosts = function (target, className) {
    target.hosts = {};
    $('.' + className).each(function () {

        target.hosts[$(this).find('p.host-name').text()] = {
            ip: $(this).find('p.host-ip').text(),
            login: $(this).find('p.host-login').text()

        };
        // $(this).find('p.host-name');
        // console.log(target.hosts);
    });
    GLOBAL_VAR = target;
};

notifyButtonById = function (btnId) {
    // self
};

$.fn.graphite.defaults.url = "https://localhost:8443/renderer/";
$.fn.graphite.defaults.width = "450";
$.fn.graphite.defaults.height = "300";


$('#btnFixImage').click(function () {
    console.log("btnFixImage");
    function openNewBackgroundTab(url) {
        var a = document.createElement("a");
        a.href = url;
        var evt = document.createEvent("MouseEvents");

        evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0,
            true, false, false, false, 0, null);
        a.dispatchEvent(evt);
    }

    var url = prompt("Please enter graphite: [ip:port]", "10.30.103.95:8443");
    if (url != null) {
        console.log('Dispatch openNewWindow');
        openNewBackgroundTab('https://' + url + '/renderer/?from=-1d&height=300&until=now&width=450&target=carbon.agents.vagrant-ubuntu-trusty-64-1.memUsage&title=CPUMonitor&_t=0.013591398485004902');
    }

});

console.log(GLOBAL_VAR);


console.log("init.js/OK");