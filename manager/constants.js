function define(name, value) {
    Object.defineProperty(exports, name, {
        value: value,
        enumerable: true
    });
}

var os  = require('os');
var ifaces = os.networkInterfaces();

var eth0IP = undefined;

Object.keys(ifaces).forEach(function (ifname) {
    var alias = 0;

    ifaces[ifname].forEach(function (iface) {
        if ('IPv4' !== iface.family || iface.internal !== false) {
            // skip over internal (i.e. 127.0.0.1) and non-ipv4 addresses
            return;
        }

        if (alias >= 1) {
            // this single interface has multiple ipv4 addresses
            console.log(ifname + ':' + alias, iface.address);
        } else {
            // this interface has only one ipv4 adress
            console.log(ifname, iface.address);
            if(ifname === "eth0"){
                eth0IP = iface.address;
            }
        }
        ++alias;
    });
});


define("PI", 3.14);
define("rmq_url", 'amqp://benchbox:benchbox@'+eth0IP+'/'); // amqp
define("influx", {
    client_metrics: {
        host: 'localhost',
        port: 8086,
        username: 'root',
        password: 'root',
        database: 'metrics',
    },
    server_metrics: {
        host: 'localhost',
        port: 8086,
        username: 'root',
        password: 'root',
        database: 'server_metrics',
    },
    db: {
        name: 'metrics',
        user: 'test',
        pass: 'test'
    },
    influx_conn: {
        host: 'localhost',
        port: 8086,
        protocol: 'http',
        username: 'root',
        password: 'root',
        database: 'metrics'
    }
}); // influx


define('mongodb_url', 'mongodb://localhost:27017/benchbox'); // mongo