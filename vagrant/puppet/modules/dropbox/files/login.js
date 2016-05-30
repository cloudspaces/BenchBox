
console.log("LOGIN!!!");
// this script will login to at the dropbox login page using phantom js

/*
var items = (document.getElementsByTagName("form"));

for(var key in items){
    var dom = items[key]

    if(dom.action === "https://www.dropbox.com/cli_link_nonce")
    {
        // fill the form here
        console.log(dom)
        test = dom

        var inputs = dom.getElementsByClassName('text-input-wrapper')
        console.log(inputs)
        for(var idx in inputs){
            var input =  inputs[idx];

            if(input instanceof HTMLElement)
            {
                var field = input.getElementsByTagName('input');
                var input_field = field[0];
                console.log(input_field)
                var str = input_field.getAttribute("type");
                switch (str){
                    case "email":
                        input_field.value = "benchbox@outlook.com";
                        break;
                    case "password":
                        input_field.value = "salou2010";
                        break;
                    default:
                        console.log("MISSING ATTR", str);
                        break;
                }
            }else {
                //noop
            }
        }

        dom.getElementsByClassName("login-button")[0].click()
    }
}
    */