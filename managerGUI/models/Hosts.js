var mongoose = require('mongoose');

var HostSchema = new mongoose.Schema({
    hostname: {type: String, default: 'toSet'},
    ip:  {type: String, default: 'localhost'},
    logging: {type: String, default: 'milax'},
    profile: {type: String, default:'sync', enum : ['sync', 'idle', 'cdn', 'backup', 'regular']},
    cred_stacksync: {type: String, default:'None'},
    cred_owncloud: {type: String, default:'None'},
    note: {type: String, default:'deim1', enum : ['deim1', 'deim2', 'deim3']},
    updated_at: {type: Date, default: Date.now}
});


module.exports = mongoose.model('Host', HostSchema);