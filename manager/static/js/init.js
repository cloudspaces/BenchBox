console.log("init.js");

bugall = null;
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
                testOperation: 'keepalive', // default monitor operation
                testMonitor: 'keepalive' // default execute operation
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
                            $.notify(changeDummy, 'success');
                            $scope.hosts[idx].status = item.status
                        }
                        if ($scope.hosts[idx].status_sandbox !== item.status_sandbox) {
                            var changeSandBox = " [changed sandbox] from:  " + $scope.hosts[idx].status_sandbox + " to " + item.status_sandbox;
                            console.log(changeSandBox);
                            $.notify(changeSandBox, 'success');
                            $scope.hosts[idx].status_sandbox = item.status_sandbox
                        }
                        if ($scope.hosts[idx].status_benchbox !== item.status_benchbox) {
                            var changeBenchBox = " [changed] benchbox from:  " + $scope.hosts[idx].status_benchbox + " to " + item.status_benchbox;
                            console.log(changeBenchBox);
                            $.notify(changeBenchBox, 'success');
                            $scope.hosts[idx].status_benchbox = item.status_benchbox
                        }

                    })
                });


                // emit keepalive requests



            }

            $scope.saveFromFile = function(){
                console.log("Save from file")
                var profileFile = document.getElementById("profileFile"); // <input> myFile
                var profileList = document.getElementById("profileFileOutput"); // <div> output


                var myFile = profileFile.files[0];
                //
                var reader = new FileReader();
                // register listener on load file

                reader.onload = function(e){
                    // profileList.innerHTML = reader.result;
                    // console.log(reader.result);

                    // save for each line
                    var validHosts = [];
                    var lines = reader.result.split("\n");
                    lines.forEach(function(item, idx, all){
                        // console.log(idx, item)
                        if(item.substring(0,1) == "#"){
                            // console.log("skipped")
                        }else{
                            if(item.length == 0){
                                // console.log("empty")
                            }else {
                                try {
                                    var host = eval("("+item+")");
                                    validHosts.push(host)
                                }catch (err){
                                    console.error("unhandled format, it has to be a object castable into object")
                                }
                            }
                        }
                    });
                    console.log(validHosts);

                    // inject valid hosts into mongodb
                    if(validHosts.length == 0){
                        $.notify("No operation performed!", "info")
                    }else {
                        validHosts.forEach(function(item, idx){
                            var host = new Hosts(item);
                            host.$save(function () {
                                $scope.hosts.push(host);
                            });
                        });
                        $.notify("Please refresh the window!", "success")
                    }
                };

                reader.readAsText(myFile);

            };

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


            $scope.getMetrics = function(index){
                var host = $scope.hosts[index];
                console.log(host);
                //
                console.log("Download the metrics of this host: ", host.hostname);
                queryDownloadInfluxMeasurement(host.hostname);

                // invoke ajax request to the node server, the server does influx query and returns the result as ajax response.
            };

            $scope.resetMetrics = function(index){
                var host = $scope.hosts[index];
                console.log(host);
                //
                console.log("Drop measurement: ", host.hostname);
                queryDropInfluxMeasurement(host.hostname);

            };

            $scope.resetStatus = function(index){
                var host = $scope.hosts[index];
                console.log(host);
                console.log("Reset the host status to None at mongodb");

                host.status_benchbox = undefined;
                host.status_sandbox = undefined;
                host.status = undefined;

                Hosts.update({id: host._id}, host);

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

            /**
             * Name is the name of the DOM element where to lookup for target hosts
             * Cmd => indica que subcola de rabbit va a ejecutar las operaciones.
             * @param name, [test-check|]
             * @param cmd, [setup|vagrantUp|vagrantProvision]
             */
            $scope.rmq = function (name, cmd) {
                console.log(arguments);
                var hosts = Array.prototype.slice.call(arguments, 2); // 3r till n are the target hosts
                //console.log(hosts);
                //console.log($scope.run.testOperation);
                //console.log($scope.run);

                // setup testFolder
                switch($scope.run.testClient){
                    case "StackSync":
                        $scope.run.testFolder = "stacksync_folder";
                        break;
                    case "Dropbox":
                        $scope.run.testFolder = "Dropbox";
                        break;
                    case "OwnCloud":
                        $scope.run.testFolder = "owncloud_folder";
                        break;
                    case "Mega":
                        $scope.run.testFolder = "mega_folder";
                        break;
                    default:
                        console.log("UNHANDLED PERSONAL_CLOUD!!!");
                        return;
                        break;
                }
                console.log($scope.run.testClient);
                console.log($scope.run.testFolder);

                if(cmd == 'execute'){
                    cmd = $scope.run.testOperation; // esto no existe.
                }

                // hardcoded queue multiplexing
                switch (cmd){
                    case 'executor':
                        // handle benchBox - execute
                        cmd = $scope.run.testOperation; // hello / warmup / start / stop
                        break;
                    case 'monitor':
                        // handle sandBox - monitor
                        cmd = $scope.run.testMonitor;   // hello / warmup / start / stop
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

queryDownloadInfluxMeasurement = function(measurement){
    console.log("Download measurement: ", measurement);
    $.ajax({
        url: 'http://localhost:'+location.port+"/influx/query",
        data: {query: "select * from "+measurement},
        timeout: 6000000,
        type: 'GET',
        dataType: 'json',
        success: function(data){
            // download json as csv file
            console.log("influx response: ");
            $.notify("Success influx query",'success');
            // console.log(data);
            var milliseconds = (new Date).getTime();
            var withHeader = true;
            var output_name = "report_"+measurement+"_"+milliseconds;
            JSONToCSVConvertor(data[0], output_name, withHeader);
        },
        error: function(err){
            console.log(err);
            $.notify('Error! ' + err, 'error');
        }
    })
};
queryDropInfluxMeasurement = function(measurement){
    $.ajax({
        url: 'http://localhost:'+location.port+"/influx/query",
        data: {query: "drop measurement "+measurement},
        timeout: 6000000,
        dataType: 'json',
        type: 'GET',
        success: function(data){
            // download json as csv file
            console.log("influx response: ");
            $.notify("Success DROP "+measurement+"query",'success');
        },
        error: function(err){
            $.notify('Measurement '+measurement+' is clean! ', 'info');
        }
    })
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
        cred_dropbox: host.cred_dropbox,
        cmd: cmd,
        target_queue: host.rmq_queue,
        test: host.test_setup
    };

    appendAllParams(args, 'bb-config');
    appendAllHosts(args, 'bb-hosts');
    //console.log("ARGS::::::");
    //console.log(args);
    $.ajax({
        url: 'http://localhost:'+location.port+'/rmq/emit',
        data: args,
        timeout: 6000000, // 6000s ::100min
        type: 'GET',
        success: function (data) {
            //console.log(args);
            console.log("Success, rmq!");
            console.log(data);
            $.notify('Success rmq: ['+args.target_queue+"] " + host.hostname + ' ' + cmd, 'success');
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
        cred_dropbox: host.cred_dropbox,
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


function JSONToCSVConvertor(JSONData, ReportTitle, ShowLabel) {
    //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
    // console.log("JSONTOCSVConverter",JSONData);
    var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;

    var CSV = '';
    //Set Report title in first row or line

    // CSV += ReportTitle + '\r\n\n';

    //This condition will generate the Label/Header
    if (ShowLabel) {
        var row = "";

        //This loop will extract the label from 1st index of on array
        for (var index in arrData[0]) {

            //Now convert each value to string and comma-seprated
            row += index + ',';
        }

        row = row.slice(0, -1);

        //append Label row with line break
        CSV += row + '\r\n';
    }

    //1st loop is to extract each row
    for (var i = 0; i < arrData.length; i++) {
        var row = "";

        //2nd loop will extract each column and convert it in string comma-seprated
        for (var index in arrData[i]) {
            //row += '"' + arrData[i][index] + '",';
            row += arrData[i][index] + ',';
        }

        row.slice(0, row.length - 1);

        //add a line break after each row
        CSV += row + '\r\n';
    }

    if (CSV == '') {
        alert("Invalid data");
        return;
    }

    //Generate a file name
    var fileName = ""; // prefix
    //this will remove the blank-spaces from the title and replace it with an underscore
    fileName += ReportTitle.replace(/ /g,"_");

    //Initialize file format you want csv or xls
    var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);

    // Now the little tricky part.
    // you can use either>> window.open(uri);
    // but this will not work in some browsers
    // or you will not get the correct file extension

    //this trick will generate a temp <a /> tag
    var link = document.createElement("a");
    link.href = uri;

    //set the visibility hidden so it will not effect on your web-layout
    link.style = "visibility:hidden";
    link.download = fileName + ".csv";

    //this part will append the anchor tag and remove it after automatic click
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}



console.log(GLOBAL_VAR);


console.log("init.js/OK");