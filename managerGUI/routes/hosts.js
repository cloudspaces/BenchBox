var express = require('express');
var router = express.Router();

var mongoose = require('mongoose');
var Host = require('../models/Hosts.js');


/* GET host listing. */
router.get('/', function(req, res, next) {

    Host.find(function(err, hosts){
        if (err) return next(err);

        console.log('found!');
        // sort corresponds to the order by func
        res.json(hosts.sort({hostname: 0, user: 0}));
        //res.json(hosts);
    });
    // res.send('respond with a resource');
});


/* POST /hosts */
router.post('/', function(req, res, next) {
    Host.create(req.body, function (err, post) {
        if (err) return next(err);
        res.json(post);
    });
});

/* GET /hosts/id */
router.get('/:id', function(req, res, next) {
    Host.findById(req.params.id, function (err, get) {
        if (err) return next(err);
        res.json(get);
    });
});


/* PUT /hosts/:id */
router.put('/:id', function(req, res, next) {
    Host.findByIdAndUpdate(req.params.id, req.body, function (err, put) {
        if (err) return next(err);
        res.json(put);
    });
});


/* DELETE /hosts/:id */
router.delete('/:id', function(req, res, next) {
    Host.findByIdAndRemove(req.params.id, req.body, function (err, post) {
        if (err) return next(err);
        res.json(post);
    });
});

module.exports = router;
