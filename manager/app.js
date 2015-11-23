var express = require('express');
var session = require('express-session');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

// var statusManager = require('');

var app = express();


// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- connecting to mongoserver -------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------


function createDBSettings(mongoLabURI) {
    var dbSettings = {},
        regexp = /^mongodb:\/\/(\w+):(\w+)@(\w+):(\w+)\/(\w+)$/,
        matches = regexp.match(mongoLabURI);
    dbSettings.dbname = matches[5];
    dbSettings.host = matches[3];
    dbSettings.port = matches[4];
    dbSettings.username = matches[1];
    dbSettings.password = matches[2];
    return dbSettings;
}
var url = 'mongodb://localhost:27017/benchbox'

var mongoose = require('mongoose');
mongoose.connect(url, function (err) {
    if (err) {
        console.log('connection to mongoose error!', err);
    } else {
        console.log('connection to mongoose successful!');
    }
});


// ------------------------------------------------------------------------
// -- load file system
// ------------------------------------------------------------------------

/*
 var fs = require('fs');
 var path = require('path');
 var filePath = path.join(__dirname, 'static/json/config.json')
 var obj;

 fs.readFile(filePath, 'utf8', function(err, data){

 if (err) throw err;
 obj = JSON.parse(data);
 console.log('configuration', obj);
 });
 */

// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- view engine setup ---------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------


app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');


// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- Middleware, ---------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------


// uncomment after placing your favicon in /public
app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, 'static')));

// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- Sessions, -----------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------


app.use(session({
    secret: 'keyboard cat',
    cookie: {
        maxAge: 60000
    },
    resave: true,
    saveUninitialized: true
}));


app.use(function (req, res, next) {
    var sess = req.session;
    if (sess.views !== undefined) {
        sess.views++
    } else {
        sess.views = 1;
    }
    next();
});


// log the client ip on every request


var routes = require('./routes/index');
var users = require('./routes/users');
var todos = require('./routes/todos');
var hosts = require('./routes/hosts');
var inits = require('./routes/init');
var homes = require('./routes/home');
var loads = require('./routes/load');
var rpcs = require('./routes/rpc');
var rmqs = require('./routes/rmq');

// api rest

app.use('/', routes);
app.use('/users', users);
app.use('/todos', todos);
app.use('/home', homes);
app.use('/hosts', hosts);
app.use('/init', inits);
app.use('/load', loads);
app.use('/rpc', rpcs);
app.use('/rmq', rmqs);


// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- connecting to rabbitmq-server -------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

var amqp = require('amqplib/callback_api');
var amqp_url = 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy';
var amqp_conn = null;
var manager_queue = 'rpc_queue';
var hostModel = require('./models/Hosts.js');
amqp.connect(amqp_url, function (err, conn) {
    if (err) {
        console.log('connection rabbitmq error', err);
    } else {
        console.log('connection rabbitmq successful!');
        amqp_conn = conn; // single connection for whole server.
    }
    conn.createChannel(function (err, ch) {
        var q = manager_queue;
        ch.assertQueue(q, {durable: false}, function (err, q) {
            console.log(' [x] Awaiting RPC requests at: [' + q.queue + ']');
        });
        ch.prefetch(1);
        ch.consume(q, function rpc_reply(msg) {
            var host_status = JSON.parse(msg.content)  // nomes el missatge esta en json
            console.log("[" + msg.properties.replyTo + "] --> [" + msg.fields.consumerTag +
                "] : host[%s] status(%s) :",
                host_status.host, host_status.status);

            var status = host_status.status
            var dummyhost = host_status.host.split('.')[0]
            var vboxhost = host_status.host.split('.')[1]
            console.log(status, dummyhost, vboxhost)
            // fer un ajax request a si mateix o modificar directament ?
            hostModel.findOne({hostname: dummyhost}, function (err, host) {
                if (err) {
                    console.error(err.message)
                }
                console.log("FOUND: ", host);

                var status_attr = 'status';
                if (dummyhost != vboxhost) {
                    status_attr += '_' + vboxhost
                }
                console.log(host)
                host[status_attr] = status;

                host.save(function (err) {
                    if (err)
                        console.log(err.message)
                })
            });

            var result = "manager Joined queue " + host_status.host + "! ";
            var callbackChannel = msg.properties.replyTo;
            var callbackMsg = new Buffer(result.toString())
            var callbackProp = {correlationId: msg.properties.correlationId}
            ch.sendToQueue(callbackChannel, callbackMsg, callbackProp); // send to queue
            ch.ack(msg); // fer un ack del message
        });
    });
});


// ------------------------------------------------------------------------
// -- setup status update
// -------------------------------------------------------------------------


// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- Visualization, ------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------


// catch 404 and forward to error handler
app.use(function (req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});


// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
    app.use(function (err, req, res, next) {
        res.status(err.status || 500);
        res.render('error', {
            message: err.message,
            error: err
        });
    });
}

// production error handler
// no stacktraces leaked to user
app.use(function (err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
        message: err.message,
        error: {}
    });
});


module.exports = app;
