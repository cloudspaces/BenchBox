/* Based on http://www.kingsquare.nl/blog/29-06-2011/16812936/Use-node.js-to-install-and-link-Dropbox-fully-automated-in-a-text-based-Linux-environment
 * Copyright (c) 2011 Kingsquare BV
 *
 * Modified by Christian G. Warden <cwarden@xerus.org>
 **/

'use strict';


var fs = require('fs');
function urlify(text) {
    var geturl = new RegExp(
        "(^|[\t\r\n])((ftp|http|https|gopher|mailto|news|nntp|telnet|wais|file|prospero|aim|webcal):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))"
        , "g"
    );
    var urls = text.match(geturl);

    console.log(text + " --> " + urls);
    if (urls == null) {
        return false;
    }

    return urls[0].replace(' ', '');
}


var spawn = require('child_process').spawn
    , exec = require('child_process').exec
    , dropboxdProcess;

if (process.argv.length < 4) {
    console.log('Please provide a username and password as parameter');
    return;
}

var die = function (error) {
    console.log(error);
    dropboxdProcess.kill();
    process.exit(1);
}

console.log('Starting dropbox-link process');
delete process.env.DISPLAY;
try {
    var email = process.argv[2];
    var passwd = process.argv[3];
    var cmd = process.env.HOME + '/.dropbox-dist/dropboxd';
    console.log('starting ' + cmd);
    dropboxdProcess = spawn(cmd);
    var index = 0;
    var alreadyCalled = false;
    var target = null;


    dropboxdProcess.stdout.on('data', function (data) {
        var resultString = String(data);


        if (target == null)
            console.log(index++, resultString);
        // comprovar lo output
        // aqui nomes entra un cop
        if (target == null) {
            var res = resultString.split(" ");
            // console.log(res);
            if (res.length == 7 && !alreadyCalled) {
                alreadyCalled = true;
                // only the first call will happen if another
                // was already running we still have to use the dropbox.url
                if (res[0] == "Another") {
                    // existeix un client dropbox corrent
                    console.log("KILL mySelf");
                    process.kill(res[4].substring(1, res[4].length - 1));
                }
                target = res[2];

                console.log(target.split('=')[1]);

                fs.writeFile('~/dropbox.url', target, function(err){
                    if(err) return console.log(err);
                    // console.log(target);

                    // 1r utilitzar curl per accedir a la plana web i descarregar el contingut en format html
                    // 2n renderitzar la visualitzación amb phantom






                    /*
                    phantom.create(function (ph) {
                        console.log("CREATE ph");
                        ph.createPage(function (page) {
                            console.log("CREATE page");
                            var target = "https://www.google.es/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8#q=nodejs+call+curl+dropbox+authentication";
                            page.open(target, function (status) {
                                console.log("opened? ", target, status);
                                if ( status !== 'success' ) {
                                    console.log(
                                        "Error opening url \"" + page.reason_url
                                        + "\": " + page.reason
                                    );
                                   // phantom.exit( 1 );
                                } else {
                                    console.log( "Successful page open!" );
                                   // phantom.exit( 0 );
                                }
                                page.evaluate(function () {
                                    return document;
                                }, function (result) {
                                    console.log('Page title is ' + result.title);
                                    console.log(result);
                                    ph.exit();
                                });
                            });
                        });
                    });
                    */

                });


                // this process can be killed until Client successfully linked event is
                // dropboxdProcess.kill()
            }
            else {
                console.log("Wait for URL")
            }
        }
        if (resultString.indexOf('Client successfully linked') >= 0) {
            console.log('All done. --> Killing dropbox process.');
            // dropbox says the client is linked before it has written the
            // sigstore.dbx file so we need to wait a bit.
            setTimeout(function () {
                dropboxdProcess.kill();
            }, 1000);
        }
    });
} catch (e) {
    console.log('Error: ' + e);
    dropboxdProcess.kill();
}

dropboxdProcess.stderr.on('data', function (data) {
    console.log("OnData --> " + String(data));
});

dropboxdProcess.on('exit', function (code) {
    console.log('dropbox process exited with code ' + code);
});
