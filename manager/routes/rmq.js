var express = require('express');
var router = express.Router();
var str_decoder = require('string_decoder').StringDecoder;

var amqp = require('amqplib/callback_api');

var hostModel = require('../models/Hosts.js');

// here im creating another connection, not sharing the main...
// produce action
router.get('/emit', function (req, res, next) {
    // parse the request arguments....
    console.log("START REQUEST ----------------------------");
    console.log(req.query);

    // connect to the rabbit server
    var amqp_url = req.query['rabbitmq-amqp'];
    amqp.connect(amqp_url, function (err, conn) {
        // create callback channel
        console.log("createChannel ");
        conn.createChannel(function (err, ch) {
            var queue_name = '';
            var queue_prop = {exclusive: true};
            console.log("assertQueue");
            ch.assertQueue(queue_name, queue_prop, function (err, q) {
                // on queue_ready
                var corr = generateUuid();
                var cmd = req.query.cmd;
                var target = req.query.hostname;
                var target_queue = target;
                if (req.query.target_queue !== '') {
                    target_queue += '.' + req.query.target_queue;
                }else{
                    target_queue += '.'+ req.query.hostname;
                }
                console.log(' [x] Requesting [' + cmd + '] to [' + target_queue + ']');

                var on_message_prop = {noAck: true};
                console.log("consume");
                ch.consume(q.queue, function (msg) {
                    // on queue_message
                    var response = msg.content.toString();
                    console.log(response);
                    if (msg.properties.correlationId == corr) {
                        console.log(' [.] Got '+response);
                        // update the dummyhost status
                        hostModel.findOne({hostname: target}, function (err, host) {
                            if (err) {
                                console.error(err.message)
                            } else {
                                console.log("-INI----------");
                                console.log(host.status);
                                console.log(host.status_sandbox);
                                console.log(host.status_benchbox);
                                console.log("-FIN----------");

                                var status_attr = 'status';
                                if(req.query.target_queue !== ''){
                                    status_attr += '_'+req.query.target_queue
                                }
                                status_attr = status_attr.toLowerCase();
                                host[status_attr] = cmd;

                                host.save(function (err) {
                                    if (err)
                                        console.log(err.message)
                                })
                            }
                        });
                        setTimeout(function () {
                            conn.close();
                            // process.exit(0)
                        }, 500);
                    }else{
                        console.log("no corr id");
                        hostModel.findOne({hostname: req.query.hostname}, function (err, host) {
                            if (err) {
                                console.error(err.message)
                            } else {
                                console.log("-INI----------");
                                console.log(host.status);
                                console.log(host.status_sandbox);
                                console.log(host.status_benchbox);
                                console.log("-FIN----------");

                                var status_attr = 'status';
                                switch(req.query.target_queue){
                                    case "monitor":
                                        status_attr+='_sandbox';
                                        break;
                                    case "executor":
                                        status_attr+='_benchbox';
                                        break;
                                    default:
                                        console.err("unhandled case");
                                        break;
                                }

                                status_attr = status_attr.toLowerCase();
                                host[status_attr] = cmd;
                                host.save(function (err) {
                                    if (err)
                                        console.log(err.message)
                                })

                            }
                        });
                        setTimeout(function () {
                            conn.close();
                            // process.exit(0)
                        }, 500);
                    }
                }, on_message_prop);
                ch.sendToQueue(target_queue, // target-hostname
                    // send rpc message to queue
                    new Buffer(JSON.stringify({cmd: cmd, msg: req.query})),
                    {
                        correlationId: corr,
                        replyTo: q.queue
                    }
                );
            });
        });
    });

    console.log("END REQUEST ----------------------------");
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
