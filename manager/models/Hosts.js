var mongoose = require('mongoose');

var HostSchema = new mongoose.Schema({
    hostname: {type: String, default: 'toSet'},
    ip:  {type: String, default: 'localhost'},
    logging: {type: String, default: 'milax'},
    profile: {type: String, default:'sync', enum : ['sync', 'idle', 'cdn', 'backup', 'regular']},
    cred_stacksync: {type: String, default:'None'},
    cred_owncloud: {type: String, default:'[user:pass] or just user'},
    cred_dropbox:{type:String,default: 'email:pass'},
    note: {type: String, default:'ast#'},
    status: {
        type: String,
        default:'idle'
        // enum : ['none','configuring','idle', 'running', 'teardown', 'halt']
    },
    status_benchbox: {
        type: String,
        default:'none'
    },
    status_sandbox: {
        type: String,
        default:'none'
     },

    updated_at: {type: Date, default: Date.now}
});
/*
none        : no se sap con esta
configuring : s'esta configurant
idle        : no s'esta fent cap operacio
running     : s'esta executant tests
teardown    : s'esta recolectant logs
halt        : la vms esta apagada
*/

module.exports = mongoose.model('Host', HostSchema);