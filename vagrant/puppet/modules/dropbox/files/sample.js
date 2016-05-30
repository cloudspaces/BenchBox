var casper = require('casper').create({
    logLevel: "info",
    verbose: true
});
console.info("Load Casper");


casper.echo("Casper CLI passed args:");
console.log(casper.cli.args);
var url = casper.cli.args[0];
var user = casper.cli.args[1];
var pass = casper.cli.args[2];

console.log(url, user, pass);
if (casper.cli.args.length !== 3) {
    console.warn("Exit more args required [url] [user] [pass]");
    casper.exit();
} else {
    casper.start(url).thenEvaluate(function(login) {
        this.echo(this.getTitle());

        console.log(document.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='login-email text-input login-text-input standard'] > div[class='text-input-wrapper'] > input[type='email']"));

        console.log("user");
        document.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='login-email text-input login-text-input standard'] > div[class='text-input-wrapper'] > input[type='email']").value = login.user;
        // set password
        console.log("pass");
        document.querySelector("form[action='/cli_link_nonce'] > div[class='credentials-form__fields'] > div[class='text-input login-password login-text-input standard'] > div[class='text-input-wrapper'] > input[type='password']").value = login.pass;
        // submit form on click
        console.log("go");
        document.querySelector("form[action='/cli_link_nonce'] > div[class='clearfix'] > button").click()

    }, {user: user, pass: pass});

    casper.run();

}