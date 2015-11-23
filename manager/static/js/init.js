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
                testProfile: 'backupsample',
                testFolder: 'stacksync_folder',
                testClient: 'StackSync'
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
                            console.log(" [changed dummyhost] from:  " + $scope.hosts[idx].status + " to " + item.status)
                            $scope.hosts[idx].status = item.status
                        }
                        if ($scope.hosts[idx].status_sandbox !== item.status_sandbox) {
                            console.log(" [changed sandbox] from:  " + $scope.hosts[idx].status_sandbox + " to " + item.status_sandbox)
                            $scope.hosts[idx].status_sandbox = item.status_sandbox
                        }
                        if ($scope.hosts[idx].status_benchbox !== item.status_benchbox) {
                            console.log(" [changed] benchbox from:  " + $scope.hosts[idx].status_sandbox + " to " + item.status_sandbox)
                            $scope.hosts[idx].status_sandbox = item.status_sandbox
                        }

                    })
                });
                /*
                 console.log($scope.currHosts)
                 angular.forEach($scope.currHosts, function(item, idx){
                 console.log(item)
                 item.status = idx+'IDLE '+ $scope.itv_time++
                 })
                 */
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
                console.info(name, cmd, ss)
                // console.log($scope)
                if (ss == undefined) {
                    console.log("Not ss cmd")
                } else {
                    console.info("ss cmd!")
                    cmd = cmd + $("#ssRadio input[type='radio']:checked")[0].value + ss;
                    console.log(cmd)
                }
                $('.' + name).each(function () {
                    // console.log(this)
                    if ($(this).prop('checked')) {
                        var checkedId = this.value;
                        var host = $scope.hosts.filter(function (item) {
                            return item._id == checkedId
                        })
                        console.log("rpcHost" + cmd, this.name, checkedId, host[0]);
                        if (cmd === 'setup') {
                            rpcHost(host[0], cmd)
                        }
                    }
                })
            };

            $scope.rmq = function (name, cmd) {
                $('.' + name).each(function () {
                    // console.log(this)
                    if ($(this).prop('checked')) {
                        var checkedId = this.value;
                        var host = $scope.hosts.filter(function (item) {
                            return item._id == checkedId
                        })
                        console.log("rmqHost: " + cmd, this.name, checkedId, host[0]);
                        rmqHost(host[0], cmd)
                    }
                })
            }

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

            $scope.runTest = function (warmup, cb) {

                console.log($scope.hosts.length);
                var test = $scope.run;

                if (warmup === undefined) {
                    test.testWarmUp = '0';
                } else {
                    test.testWarmUp = '1';
                }

                console.log(name)
                console.log(test)
                var hosts = $scope.hosts.filter(function (item) {
                    console.log(item);
                    if (item.test)
                        return item;
                });
                console.log(hosts.length);
                if (hosts.length === 0)
                    $.notify('Warning!, No host checked', 'warn');
                else
                    $.notify('Request rpcTest forwarded!', 'info');
                console.log('Hosts!!!');
                rpcTest(hosts, test);

            };

            $scope.edit = function (index) {
                console.log(index)
                console.log($scope.editing)
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
        url: 'http://localhost:3000/rpc/nmap',
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
        cmd: cmd
    };
    appendAllParams(args, 'bb-config');
    appendAllHosts(args, 'bb-hosts');
    $.ajax({
        url: 'http://localhost:3000/rmq/emit',
        data: args,
        timeout: 6000000, // 6000s ::100min
        type: 'GET',
        success: function (data) {
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
        url: 'http://localhost:3000/rpc/rpc',
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

rpcStatus = function (args, cmd, statusId, target) {
    console.log("rpcStatus");
    console.log(args, cmd, statusId, target);
    args.status = cmd;
    args.target = target;

    $.ajax({
        url: 'http://localhost:3000/rpc/status',
        data: args,
        timeout: 6000000, // 6000s ::100min
        type: 'GET',
        success: function (data) {
            console.log("RESULTS, rpcStatus!");
            console.log(data);
            console.log($('#' + statusId))
            // $('#'+statusId).children('.stats').text(data.result);
            $('#' + statusId).children('.stats').text(data);
        },
        error: function (err) {
            console.log(err);
            console.log('pc, Error ' + args + ' ' + cmd + ' ', err);
            $.notify('Error! ' + err, 'error');
        }
    });
};
rpcTest = function (hosts, test, cb) {
    console.log("RunTests ");
    console.log("Hosts: ", hosts);
    console.log("Test: ", test);

    hosts.forEach(function (host) {
        console.log(host);
        console.log('->');
        console.log(test);
        var cmd = 'test';
        var args = {
            ip: host.ip,
            hostname: host.hostname,
            login: host.logging,
            profile: host.profile,
            cred_stacksync: host.cred_stacksync,
            cred_owncloud: host.cred_owncloud,
            cmd: 'test',
            test: test
        };

        $.ajax({
            url: 'http://localhost:3000/rpc/rpc',
            data: args,
            timeout: 6000000, // 6000s ::100min
            type: 'GET',
            success: function (data) {
                console.log("Success, run test! " + (test));
                console.log(JSON.stringify(data));
                $.notify('Success! ' + host.hostname + ' ' + cmd, 'success');
            },
            error: function (err) {
                console.log(err);
                console.log('pc, Error ' + host + ' ' + cmd + ' ', err);
                $.notify('Error! ' + err, 'error');
            }
        });
    });

    /*
     if (cb !== undefined)
     cb()
     */
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
    console.log("btnFixImage")
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
        console.log('Dispatch openNewWindow')
        openNewBackgroundTab('https://' + url + '/renderer/?from=-1d&height=300&until=now&width=450&target=carbon.agents.vagrant-ubuntu-trusty-64-1.memUsage&title=CPUMonitor&_t=0.013591398485004902');
    }

});

console.log(GLOBAL_VAR);


console.log("init.js/OK");