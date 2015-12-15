var express = require('express');
var router = express.Router();



var fs = require('fs');
var path = require('path');
var filePath = path.join(__dirname, '../static/json/config.json')
var filePathTemplate = path.join(__dirname, '../static/json/config.template.json')
var obj;
var configReady = false;

fs.stat(filePath, function(err, stat){
    if(err == null){
        configReady =true;
        console.log("config.json exists");
    }else{
        fs.readFile(filePathTemplate, 'utf8', function(err, data){
            if(err) throw err;
            configReady = true;
            fs.writeFile(filePath, data, function(err, data){
                if(err){
                    console.log(err);
                }else{
                    console.log("config.json generated");
                    console.log(data)
                }
            })
        });
    }
});




var sess;
/* GET init page. */
router.get('/', function (req, res, next) {
    console.log("Load");
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    console.log('Client IP: ', ip);
    var sess = req.session;

    // si es vol permetre moficar...
    while(!configReady){
        setTimeout(function(){
            console.log("waitConfig");
        }, 1000);
    } // blocking

    fs.readFile(filePath, 'utf8', function(err, data){
        if (err) throw err;
        obj = JSON.parse(data);
        console.log('configuration', obj);
        sess.config = obj[0];
        res.render('init', {title: 'BenchBox', session: sess});
    });
});


router.post('/', function(req, res, next){

    // update the configuration

    fs.writeFile(filePath, req.config, function(err, data){

    });

});


module.exports = router;
