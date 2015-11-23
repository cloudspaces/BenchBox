var express = require('express');
var router = express.Router();


var amqp = require('amqplib/callback_api');
// var amqp_url = 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy';

var hostModel = require('../models/Hosts.js');

// here im creating another connection, not sharing the main...
// produce action
router.get('/emit', function (req, res, next) {
    // parse the request arguments....
    console.log("START REQUEST ----------------------------")
    console.log(req.query)

    // connect to the rabbit server
    var amqp_url = req.query['rabbitmq-amqp']
    amqp.connect(amqp_url, function(err, conn) {
        // create callback channel
        conn.createChannel(function(err, ch) {
            var queue_name = '';
            var queue_prop = {exclusive: true};

            ch.assertQueue(queue_name, queue_prop, function(err, q) {
                // on queue_ready
                var corr = generateUuid();
                var cmd = req.query.cmd;
                var target = req.query.hostname;
                console.log(' [x] Requesting ['+ cmd +'] to ['+target+']');

                var on_message_prop = {noAck: true}
                ch.consume(q.queue, function(msg) {
                    // on queue_message
                    if (msg.properties.correlationId == corr) {
                        console.log(' [.] Got %s', msg.content.toString());
                        setTimeout(function()
                        {
                            conn.close();
                            // process.exit(0)
                        }, 500);
                    }
                }, on_message_prop);
                ch.sendToQueue(target, // target-hostname
                    // send rpc message to queue
                    new Buffer(cmd.toString()),
                    {
                        correlationId: corr,
                        replyTo: q.queue
                    }
                );
            });
        });
    });

    console.log("END REQUEST ----------------------------")
    res.json({})
});


function generateUuid() {
    return Math.random().toString() +
        Math.random().toString() +
        Math.random().toString();
}

module.exports = router;

// EACH OF THE DUMMYHOST HAS TO HAVE AN RPC_CONSUMER
// rabbit mq producer rest api


// ..
// able to send requests to the remote dummy hosts
// where the queue name is would be the remote hostname.virtual_hostname
// ..
//
