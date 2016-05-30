var links = [];
var casper = require('casper').create();

function printContent(){
    console.log("printContent");
    return document.querySelectorAll('button');

}

function submitForm(login){
    console.log("user");
    document.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='login-email text-input login-text-input standard'] > div[class='text-input-wrapper'] > input[type='email']").value = login.user;
    // set password
    console.log("pass");
    document.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='text-input login-password login-text-input standard'] > div[class='text-input-wrapper'] > input[type='password']").value = login.pass;
    // submit form on click
    console.log("go");
    document.querySelector("form[action='/cli_link_nonce'] > div[class='clearfix'] > button").click()

}

console.log(casper.cli.args);
//var url = casper.cli.args[0];
//var user = casper.cli.args[1];
//var pass = casper.cli.args[2];

var url = "https://www.dropbox.com/cli_link_nonce?nonce=";
var nonce = casper.cli.args[0]; // "a32681beaa4101e8e0a2ca7ad9bf2a61" ;
var href = url+nonce;

console.log(href);

casper.start(href, function() {
    // search for 'casperjs' from google form
    console.log("START");
    this.evaluate(submitForm({user:"benchbox@outlook.com", pass: "salou2010"}));
});


casper.run(function() {
    // echo results in some pretty fashion
    console.log("RUN");
    this.evaluate(submitForm({user:"benchbox@outlook.com", pass: "salou2010"}));
});