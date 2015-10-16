var mongoose = require('mongoose');

var CredentialSchema = new mongoose.Schema({
    id: String,
    name: String,
    swift_account: String,
    swift_user: String,
    email: String,
    updated_at: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Credential', CredentialSchema);

/*
 id: 'd745174c-23d0-4df4-b956-3821691301a8',
 name: 'demo3',
 swift_account: 'AUTH_47f13d9fe178438580ffb08ddca763a4',
 swift_user: 'stacksync_3e456cdc_demo2',
 email: 'demo2@stacksync.org'


 --
    // storage type
 String
 Boolean
 Date
 Array
 Number
 ObjectId
 Mixed
 Buffer

 */