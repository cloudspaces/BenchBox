var express = require('express');
var router = express.Router();



var fs = require('fs');
var path = require('path');
var filePath = path.join(__dirname, '../static/json/config.json')
var obj;






var sess;
/* GET init page. */
router.get('/', function (req, res, next) {
    console.log("Load");
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    console.log('Client IP: ', ip);
    var sess = req.session;

    fs.readFile(filePath, 'utf8', function(err, data){
        if (err) throw err;
        obj = JSON.parse(data);
        console.log('configuration', obj);
        sess.config = obj[0];


        // console.log("Session load vars", JSON.stringify(sess, null , 2));
        /*
         console.log("Session", sess);
         */
        res.render('init', {title: 'Init', session: sess});

    });



});



module.exports = router;
