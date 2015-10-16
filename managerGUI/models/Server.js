var mongoose = require('mongoose');

var ServerSchema = new mongoose.Schema({
    stacksync: {ip: String, port: number},
    owncloud: {ip: String, port: number},
    graphite: {ip: String, port: number},
    impala: {ip: String, port: number},
    updated_at: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Server', ServerSchema);