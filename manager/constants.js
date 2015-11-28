function define(name, value) {
    Object.defineProperty(exports, name, {
        value:      value,
        enumerable: true
    });
}

define("PI", 3.14);
define("rmq_url", 'amqp://benchbox:benchbox@10.50.234.51/');