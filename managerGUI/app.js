var express = require('express');
var session = require('express-session');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var memCache = require('memory-cache');


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
// mongodb://dbuser:dbpass@host:port/dbname

mongoOps = {
    insertDocuments: function (db, callback) {
        // Get the documents collection
        var collection = db.collection('documents');
        // Insert some documents
        collection.insert([
            {a: 1}, {a: 2}, {a: 3}
        ], function (err, result) {
            assert.equal(err, null);
            assert.equal(3, result.result.n);
            assert.equal(3, result.ops.length);
            console.log("Inserted 3 documents into the document collection");
            callback(result);
        });
    },

    updateDocument: function (db, callback) {
        // Get the documents collection
        var collection = db.collection('documents');
        // Update document where a is 2, set b equal to 1
        collection.update({a: 2}
            , {$set: {b: 1}}, function (err, result) {
                assert.equal(err, null);
                assert.equal(1, result.result.n);
                console.log("Updated the document with the field a equal to 2");
                callback(result);
            });
    }, removeDocument: function (db, callback) {
        // Get the documents collection
        var collection = db.collection('documents');
        // Insert some documents
        collection.remove({a: 3}, function (err, result) {
            assert.equal(err, null);
            assert.equal(1, result.result.n);
            console.log("Removed the document with the field a equal to 3");
            callback(result);
        });
    }, findDocuments: function (db, callback) {
        // Get the documents collection
        var collection = db.collection('documents');
        // Find some documents
        collection.find({}).toArray(function (err, docs) {
            //assert.equal(err, null);
            //assert.equal(2, docs.length);
            console.log("Found the following records");
            console.dir(docs);
            callback(docs);
        });
    }
};


// operations...


var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');


var url = 'mongodb://test:test@ds055822.mongolab.com:55822/benchbox'


MongoClient.connect(url, function (err, db) {
    assert.equal(null, err);
    console.log("Connected correctly to server");
    /*
     // do db operations
     mongoOps.insertDocuments(db, function () {
     console.log("Document pushed to the db correctly");
     mongoOps.updateDocument(db, function () {
     console.log("Document update correctly");
     mongoOps.removeDocument(db, function () {
     console.log("Document removed successfully");
     mongoOps.findDocuments(db, function() {
     console.log("Document found!");
     db.close();
     });
     })
     });
     });
     */
});


// another mongodb client

var mongoose = require('mongoose');
mongoose.connect(url, function (err) {
    if (err) {
        console.log('connection error', err);
    } else {
        console.log('connection successful');
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
    cookie:
    {
        maxAge: 60000
    },
    resave: true,
    saveUninitialized: true
}));


app.use(function(req, res, next) {
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

// api rest

app.use('/', routes);
app.use('/users', users);
app.use('/todos', todos);
app.use('/home', homes);
app.use('/hosts', hosts);
app.use('/init', inits);
app.use('/load', loads);
app.use('/rpc', rpcs);



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
