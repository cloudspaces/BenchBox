var express = require('express');
var router = express.Router();
var zerorpc = require('zerorpc');
var client = new zerorpc.Client({
    timeout: 3000,  // Sets the number of seconds to wait for a response before considering the call timed out. Defaults to 30.
    heartbeatInterval: 100000 // Sets the number of miliseconds to send send heartbeats to connected servers. Defaults to 5000ms.
});

var requestIndex = 0;
client.connect('tcp://127.0.0.1:4242');

/* GET manager rpc page. */
router.get('/nmap', function (req, res, next) {
    var cmd = req.url.split('=')[1].replace(/\+/g, ' ');
    console.log("NMAP: " + cmd);
    client.invoke('nmap', cmd.split(' ')[1], cmd.split(' ')[0], function (error, resp, more) {
        if (error) {
            console.error("NMAP Error:", cmd, error)
        }
        console.log(resp);
        res.json({result: JSON.stringify(resp)})
    });
});

/* GET manager rpc page. */
router.get('/cmd', function (req, res, next) {
    var cmd = req.url.split('=')[1].replace(/\+/g, ' ');
    console.log("CMD: " + cmd);
    (client.invoke('cmd', cmd, function (error, resp, more) {
        if (error) {
            console.log("CMD Error:", cmd, error)
        }
        res.json({result: JSON.stringify(resp)})
    }));

});


module.exports = router;
