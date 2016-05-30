var express = require('express');
var router = express.Router();
var str_decoder = require('string_decoder').StringDecoder;
var constants = require("../constants");
var influx = require('influx');

var influxClient = influx(constants.influx.client_metrics);

// here im creating another connection, not sharing the main...
// produce action

router.get('/query', function (req, res, next) {
    console.log("A Influx query Request received !");
    console.log(req.query);
    var query = req.query;
    influxClient.query(query.query, function(err, result){
        if (err){
            console.log(err);
        }
        // console.log(result);
        res.json(result);
    })
});



module.exports = router;

// EACH OF THE DUMMYHOST HAS TO HAVE AN RPC_CONSUMER
// rabbit mq producer rest api


// ..
// able to send requests to the remote dummy hosts
// where the queue name is would be the remote hostname.virtual_hostname
// ..
//
