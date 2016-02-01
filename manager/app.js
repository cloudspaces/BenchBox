var express = require('express');
var session = require('express-session');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var constants = require("./constants");

var influx = require('influx');


var app = express();


// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// -- connecting to influxdb  ---------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

// console.log(constants.influx.influx_conn);

var influxClient = influx(constants.influx.server);
var influxReady = false;
influxClient.getDatabaseNames(function(err, arrDBS){

    if(err)
        throw err;
    if(arrDBS.indexOf(constants.influx.influx_conn.database) > -1){
        console.log("Database ["+constants.influx.influx_conn.database+"] ready!" );
        influxReady = true;
        return;
    }

    influxClient.createDatabase(constants.influx.influx_conn.database, function(err, result){
        if(err) throw err;
        console.log("Database created ready");
        influxReady = true;
    });
});


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

var mongoose = require('mongoose');
mongoose.connect(constants.mongodb_url, function (err) {
    if (err) {
        console.log('connection to mongoose error!', err);
    } else {
        console.log('connection to mongoose successful!');
    }
});



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
// -- connecting to rabbitmq-server ---------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

var amqp = require('amqplib/callback_api');
var amqp_url = constants.rmq_url;
var amqp_conn = null;
var manager_queue = 'rpc_queue';
var hostModel = require('./models/Hosts.js');

// this chunk of code should go withing a separate file export and required...
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
            console.log(' [' + q.queue + '] Awaiting RPC...');
        });
        ch.prefetch(1);
        ch.consume(q, function rpc_reply(msg) {
            var host_status = JSON.parse(msg.content);  // nomes el missatge esta en json
            console.log("[" + msg.properties.replyTo + "] --> [" + msg.fields.consumerTag +
                "] : host[%s] status(%s) :",
                host_status.host, host_status.status);

            var status = host_status.status;
            var dummyhost = host_status.host.split('.')[0];
            var vboxhost = host_status.host.split('.')[1].toLowerCase();
            console.log(status, dummyhost, vboxhost);
            hostModel.findOne({hostname: dummyhost}, function (err, host) {
                if (err) {
                    console.error(err.message)
                }

                var status_attr = 'status';
                if (dummyhost != vboxhost) {
                    status_attr += '_' + vboxhost
                }
                host[status_attr] = status;

                host.save(function (err) {
                    if (err)
                        console.log(err.message)
                })
            });

            var result = "manager Joined queue " + host_status.host + "! ";
            var callbackChannel = msg.properties.replyTo;
            var callbackMsg = new Buffer(result.toString());
            var callbackProp = {correlationId: msg.properties.correlationId};
            ch.sendToQueue(callbackChannel, callbackMsg, callbackProp); // send to queue
            ch.ack(msg); // fer un ack del message
        });
    });

    // ------------------------------------------------------------------------
    // -- Metrics RabbitMQ handlers :: forward to influxdb # & impala TODO
    // -------------------------------------------------------------------------

    conn.createChannel(function (err, ch) {
        var ex = 'metrics';
        ch.assertExchange(ex, 'fanout', {durable: false});

        ch.assertQueue('', {exclusive: true}, function (err, q) {
            console.log(' [' + ex + '] waiting for connection');
            ch.bindQueue(q.queue, ex, '');
            ch.consume(q.queue, function (msg) {
                // console.log(" [" + ex + "] " + msg.content.toString());
                /*
                var point = {
                    time: new Date(),
                    value: Math.floor(Math.random() * 100) + 1,
                    cpu: Math.floor(Math.random() * 100) + 1,
                    ram: Math.floor(Math.random() * 100) + 1,
                    net: Math.floor(Math.random() * 100) + 1
                };
                */
                var data = JSON.parse(msg.content);
                var metrics = data.metrics;
                var tags = data.tags;
                var point = metrics;
                var hostname = msg.fields.routingKey;
                if(influxReady){
                    influxClient.writePoint(hostname, point, tags, function(){
                    //   console.log("done writing");
                    });
                }
            }, {noAck: true}); // ignore if none reached, none blocking queue
        })
    })
});


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