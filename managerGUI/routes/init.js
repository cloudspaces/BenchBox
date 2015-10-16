var express = require('express');
var router = express.Router();


/* GET init page. */
router.get('/', function (req, res, next) {
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    console.log('Client IP: ', ip);
    var sess = req.session;

    // console.log("Session load vars", JSON.stringify(sess, null , 2));

   res.render('init', {title: 'Init', session: sess});
});



module.exports = router;
