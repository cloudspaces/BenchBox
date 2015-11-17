console.log("init.js");


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
    .controller('HostDetailCtrl', ['$scope', '$routeParams', 'Hosts', '$location', function ($scope,
                                                                                             $routeParams, Hosts, $location) {
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
    .controller('HostController', ['$scope', 'Hosts', function ($scope, Hosts) {
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
        $scope.hosts = Hosts.query(); // llistat de tots els hosts

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
            if (cmd !== 'warmUp') {
                $('.' + name).each(function () {
                    // console.log(this)
                    if ($(this).prop('checked')) {
                        var checkedId = this.value;
                        var host = $scope.hosts.filter(function (item) {
                            return item._id == checkedId
                        })


                        console.log("rpcHost" + cmd, this.name, checkedId, host[0]);
                        rpcHost(host[0], cmd)
                        // rpcHost(host[0], cmd, addStatusScope)

                    }
                })
            } else {
                console.log("warmUp" + cmd);
                $scope.runTest(cmd)
            }
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
var statusIdx = 0;

function addStatusScope(args) {
    // console.log(args);
    var name = args.ip + ':' + args.cmd;
    var statusId = "stat_" + statusIdx++;
    $("#requestStatus").append("<div class='row' id=" + statusId + "><div class='col-md-4'>" + name + " : " + statusId + "</div><div class='col-md-8 stats'>liveRpcFeedBack</div></div>");
    var statusCmd;
    // alert(args.cmd)
    switch (args.cmd) {
        case "setup":
            args.target = 'localhost'
            statusCmd = 'hostname; grep -q ss.*.key; echo $?\?; ';
            break;
        case "vagrantUp":
            args.target = 'localhost';
            statusCmd = 'hostname; VBoxManage list runningvms | [ $(wc -l) -eq 2 ]; echo $?\?; ';
            break;
        case "warmUp":
            args.target = 'benchBox';
            statusCmd = 'hostname; [ -d output ]; echo $?\?; '
            break;
        case "tearDown":
            args.target = 'benchBox';
            statusCmd = 'hostname; [ ! -d output ]; echo $?\?; '
            break;
        case "vagrantDown":
            args.target = 'localhost';
            statusCmd = 'hostname; VBoxManage list runningvms | [ $(wc -l) -eq 0 ]; echo $?\?; ';
            break;
        case "monitorUp":
            args.target = 'sandBox';
            statusCmd = 'hostname; pgrep python > /dev/null; echo $?\?; ';
            // how to check if the sandBox monitor listener is running?
            // check if an python process is running
            //
            break;
        case "clientStackSyncUp":
            statusCmd = 'hostname; pgrep java > /dev/null; echo $?\?; ';
            args.target = 'sandBox';
            // check there is no java process running
            break;
        case "clientStackSyncDown":
            statusCmd = 'hostname; pgrep java > /dev/null; [ $? -ne 0 ]; echo $?\?; ';
            args.target = 'sandBox';
            // check there is java process running
            break;
        case "clientOwncloudUp":
            statusCmd = 'hostname; echo 0\?; ';
            args.target = 'sandBox';
            break;
        case "execute":
            // check if the execute procedure is still running at the benchBox machine.
            statusCmd = 'hostname; pgrep python > /dev/null; [ $? -ne 0 ]; echo $?\?; ';
            args.target = 'benchBox';
            break;
        default:
            console.log(args.cmd);
            statusCmd = 'hostname; echo $?\?';
            break;
    }

    console.log(args);
    // args.target = 'sandBox';

    var finish = false;
    var itvTimeout = 0;
    var itvMax = 1; // 6000 * 3 = 18000 segundos
    var itvTimer = 3000;
    var statusItv = setInterval(function () {
        console.log(itvTimeout);
        itvTimeout++;
        if (finish === true) {
            $('#' + statusId).remove();
            clearInterval(statusItv);
        }
        if (itvTimeout === itvMax) {
            finish = true;
            $.notify('ExitTryLimit', 'warn')
        } else {
            switch (args.target) {
                case 'sandBox':
                    console.warn('sandBox');
                    rpcStatus(args, statusCmd, statusId, 'sandBox');
                    break;

                case 'benchBox':
                    console.warn('benchBox');
                    rpcStatus(args, statusCmd, statusId, 'benchBox');

                    break;
                default:
                    console.warn('localhost');
                    rpcStatus(args, statusCmd, statusId, 'localhost');
                    break;
            }

            var currStatus = $('#' + statusId).children('.stats').text();
            var notFound = "-1"
            console.log(currStatus)
            if (currStatus.indexOf('0?') == notFound) {
                console.warn('Still not found!');
                if (currStatus.indexOf('No route to host') == notFound) {
                    console.log('Waiting' + statusId);
                } else {
                    console.error('First setup vagrant up');
                    $.notify('Require vagrantUp: ' + statusId + args.cmd, 'error');
                    finish = true;
                }
            } else {
                console.info('StatusId: ' + statusId + ' Completed!');
                finish = true; // por que se ha encontrado un exit code zero
                $.notify('SuccessStatus: ' + statusId + args.cmd, 'success');
            }

        }
    }, itvTimer);
}

$('#btnHello').click(
    function () {
        console.log("Say hello");
        $.get('http://localhost:3000/rpc/hello', {}, function (data) {
            console.log("success hello");
            console.log(JSON.stringify({data: data}));
        });
        console.log("Fin hello");
    });


$('#btnCmd').click(
    function () {

        console.log("Run cmd");

        $.get('http://localhost:3000/rpc/cmd',
            {cmd: $('#inputCmd').val()},
            function (data) {
                console.log("success hello!!!!!!!!!!!!!!!!!!!!!!!!!!");
                writeToLogger('loggerFrame', data);
            });
        console.log("Success, run cmd!");
    });

$('#btnStart').click(
    function () {
        console.log("Run start");
        $.ajax({
            url: 'http://localhost:3000/rpc/start',
            type: 'GET',
            success: function () {
                console.log("Success, run start!");
            },
            error: function () {

            }
        });
    });

$('#btnGoodbye').click(
    function () {
        console.log("Say goodbye");
        $.ajax({
            url: 'http://localhost:3000/rpc/goodbye',
            type: 'GET',
            success: function () {
                console.log("Success, say goodbye!");
            }
        });
    });

$('#btnList').click(
    function () {
        console.log("Get list");
        $.ajax({
            url: 'http://localhost:3000/rpc/list',
            type: 'GET',
            success: function (data) {
                console.log("Success, say list!");
                console.log(data);
                writeToLogger('loggerFrame', data);
            }
        });
    });

writeToLogger = function (loggerID, lines) {
    data = lines;
    // clear logger content
    $('#' + loggerID).val('');
    lines = JSON.parse(data.result);

    // publish new data
    console.log(lines);
    console.log("Show");
    lines.forEach(function (line, idx) {
        console.log(line);
        if (line !== '')
            $('#' + loggerID).val($('#' + loggerID).val() + line + '\n');
    });
    $('#' + loggerID).scrollTop($('#' + loggerID)[0].scrollHeight);
};


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

try {
    /*
     $('#monitorCPU').graphite({
     // url: "http://myserver/render/",
     from: "-1d",
     target: [
     "carbon.agents.vagrant-ubuntu-trusty-64-1.memUsage"
     ],
     title: "CPUMonitor"
     });
     $('#monitorXXX').graphite({
     // url: "http://myserver/render/",
     from: "-1hours",
     target: [
     "carbon.agents.vagrant-ubuntu-trusty-64-1.cpuUsage"
     ],
     title: "XXXMonitor"
     });


     $('#monitorRAM').graphite({
     // url: "http://myserver/render/",
     from: "-1hours",
     target: [
     "carbon.agents.vagrant-ubuntu-trusty-64-1.memUsage"
     ],
     title: "RamMonitor"
     });

     $('#monitorNET').graphite({
     // url: "http://myserver/render/",
     from: "-1hours",
     colorList: 'red,green',
     target: [
     "alias(carbon.agents.vagrant-ubuntu-trusty-64-1.pointsPerUpdate, 'pointsPerUpdate')",
     "alias(carbon.agents.vagrant-ubuntu-trusty-64-1.updateOperations, 'updateOps')"
     ],
     title: "NetworkMonitor"
     });
     */
    console.log("do grephite");
} catch (err) {
    console.warn('Error happened', JSON.stringify(err));
}

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