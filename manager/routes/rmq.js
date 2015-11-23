var express = require('express');
var router = express.Router();


var amqp = require('amqplib/callback_api');
var amqp_url = 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy';

var hostModel = require('./model/Hosts.js');

// here im creating another connection, not sharing the main...
// produce action
router.get('/emit', function (req, res, next) {
    // parse the request arguments....
    amqp.connect(amqp_url, function(err, conn) {
        conn.createChannel(function(err, ch) {
            ch.assertQueue('', {exclusive: true}, function(err, q) {
                var corr = generateUuid();
                console.log(corr);
                var num = parseInt(args[0]);

                console.log(' [x] Requesting fib(%d)', num);

                ch.consume(q.queue, function(msg) {
                    if (msg.properties.correlationId == corr) {
                        console.log(' [.] Got %s', msg.content.toString());
                        setTimeout(function() { conn.close(); process.exit(0) }, 500);
                    }
                }, {noAck: true});

                ch.sendToQueue('rpc_queue',
                    new Buffer(q.toString()),
                    { correlationId: corr, replyTo: q.queue });
            });
        });
    });


});


function generateUuid() {
    return Math.random().toString() +
        Math.random().toString() +
        Math.random().toString();
}


// EACH OF THE DUMMYHOST HAS TO HAVE AN RPC_CONSUMER
// rabbit mq producer rest api


// ..
// able to send requests to the remote dummy hosts
// where the queue name is would be the remote hostname.virtual_hostname
// ..
//
