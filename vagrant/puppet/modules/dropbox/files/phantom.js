var args = require('system').args;
var page = require('webpage').create();


console.log(args);
var ref = "https://marketing.dropbox.com/cli_link_nonce?referrer=";
var url = args[1];
var user = args[2];
var pass = args[3];
console.log(url, user, pass);

page.onConsoleMessage = function (msg, lineNum, sourceId) {
    console.log('CONSOLE: ' + msg + ' (from line #' + lineNum + ' in "' + sourceId + '")');
};


page.open(ref, function (status) {

    console.log("Page loaded", status);

    page.onConsoleMessage = function (msg, lineNum, sourceId) {
        console.log('CONSOLE: ' + msg + ' (from line #' + lineNum + ' in "' + sourceId + '")');
    };

    // console.log(page.content);
    page.evaluate(function () {


        console.log(document.title);
        console.log("Evaluate forms");
        console.log(document.getElementsByTagName('form'));
        var forms = document.getElementsByTagName('form');



        console.log("user");
        // page.content.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='login-email text-input login-text-input standard'] > div[class='text-input-wrapper'] > input[type='email']").value = "ASDF";
        // set password
        console.log("pass");
        //document.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='text-input login-password login-text-input standard'] > div[class='text-input-wrapper'] > input[type='password']").value = login.pass;
        // submit form on click
        console.log("go");
        // document.querySelector("form[action='/cli_link_nonce'] > div[class='clearfix'] > button").click()



        console.log("END");
    });


});