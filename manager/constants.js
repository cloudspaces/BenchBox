function define(name, value) {
    Object.defineProperty(exports, name, {
        value: value,
        enumerable: true
    });
}

define("PI", 3.14);
define("rmq_url", 'amqp://benchbox:benchbox@10.30.236.141/'); // amqp
define("influx", {
    server: {
        host: 'localhost',
        port: 8086,
        username: 'root',
        password: 'root',
        database: 'metrics',
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


define('mongodb_url', 'mongodb://localhost:27017/benchbox') // mongo