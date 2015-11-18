var express = require('express');
var router = express.Router();
var queryString = require('query-string');
var zerorpc = require('zerorpc');
var client = new zerorpc.Client({
    timeout: 3000,  // Sets the number of seconds to wait for a response before considering the call timed out. Defaults to 30.
    heartbeatInterval: 100000 // Sets the number of miliseconds to send send heartbeats to connected servers. Defaults to 5000ms.
});
client.connect('tcp://127.0.0.1:4242');


/* GET manager rpc page. */
router.get('/goodbye', function (req, res, next) {
    client.invoke('goodbye', "Goodbye", function (error, resp, more) {
        if (error) {
            console.log("Error:", error)
        }
        console.log(resp);
    });
});


/* GET manager rpc page. */
router.get('/hello', function (req, res, next) {
    client.invoke('hello', "Hello", function (error, resp, more) {
        if (error) {
            console.log("Error:", error)
        }
        console.log(resp);
        res.json(resp)
    });
});


/* GET manager rpc/rpc page.
* None Blocking Wait Response
* */
router.get('/rpc', function (req, res, next) {
    console.log('/rpc/rpc');
    var fullUrl = req.protocol + '://' + req.get('host') + req.originalUrl;

    console.log("LETS SPAWNN------------------>>>>>>>");
    try {
        client.invoke('rpc', fullUrl, function (error, resp, more) {
            if (error) {
                console.log("Error:", error)
            }
        });
    }catch(err){
        console.log(err.message)
    };
    console.log("END SPAWN-------------------<<<<<<<");
    res.json({});
});



/* GET manager rpc/status page.
* Blocking wait response
* */
router.get('/status', function (req, res, next) {
    // el servidor rep una peticio get,
    console.log('/rpc/status');
    var fullUrl = req.protocol + '://' + req.get('host') + req.originalUrl;

    try {
        client.invoke('status', fullUrl, function (error, resp, more) {
            if (error) {
                console.log("Error:", error)
            }
            console.log("Result: ---------------------");
            console.log(resp);
            console.log("ResultEnd: ------------------");
            res.json(resp);
        });
    }catch(err){
        console.log(err.message);
        res.json(err.message)
    };
});

/* GET manager rpc page. */
router.get('/start', function (req, res, next) {
    client.invoke('start', "Start", function (error, resp, more) {
        if (error) {
            console.log("Error:", error)
        }

        res.json(resp)
    });
});


/* GET manager rpc page. */
router.get('/nmap', function (req, res, next) {
    var cmd = req.url.split('=')[1].replace(/\+/g, ' ');
    console.log("COMMAND: " + cmd);
    client.invoke('nmap', cmd.split(' ')[1], cmd.split(' ')[0], function (error, resp, more) {
        if (error) {
            console.log("Error:", error)
        }
        console.log(resp);
        res.json({result: JSON.stringify(resp)})
    });
});


/* GET manager rpc page. */
router.get('/list', function (req, res, next) {
    client.invoke('list', "~", function (error, resp, more) {
        if (error) {
            console.log("Error:", error)
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
