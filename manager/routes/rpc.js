var express = require('express');
var router = express.Router();

var zerorpc = require('zerorpc');

var client = new zerorpc.Client({
    timeout: 30000,  // Sets the number of seconds to wait for a response before considering the call timed out. Defaults to 30.
    heartbeatInterval: 100000 // Sets the number of miliseconds to send send heartbeats to connected servers. Defaults to 5000ms.
});

var requestIndex = 0;
client.connect('tcp://127.0.0.1:4242');



/* GET manager rpc/rpc page.
* None Blocking Wait Response
* */
router.get('/rpc', function (req, res, next) {
    console.log('/rpc/rpc '+requestIndex++);
    var fullUrl = req.protocol + '://' + req.get('host') + req.originalUrl;
    try {
        client.invoke('rpc', fullUrl, function (error, resp, more) {
            if (error) {
                console.log("Error:", error)
            }
        });
    }catch(err){
        console.log(err.message)
    };
    res.json({});
});




/* GET manager rpc page. */
router.get('/nmap', function (req, res, next) {
    var cmd = req.url.split('=')[1].replace(/\+/g, ' ');
    console.log("NMAP: " + cmd);
    client.invoke('nmap', cmd.split(' ')[1], cmd.split(' ')[0], function (error, resp, more) {
        if (error) {
            console.error("Error:", error)
        }
        console.log(resp);
        res.json({result: JSON.stringify(resp)})
    });
});



/* GET manager rpc page. */
router.get('/cmd', function (req, res, next) {
    var cmd = req.url.split('=')[1].replace(/\+/g, ' ');
    console.log("COMMAND: " + cmd);
    (client.invoke('cmd', cmd, function (error, resp, more) {
        if (error) {
            console.log("Error:", error)
        }
        res.json({result: JSON.stringify(resp)})
    }));

});


module.exports = router;
