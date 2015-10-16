var mongoose = require('mongoose');

var TodoSchema = new mongoose.Schema({
    name: {type: String, default: 'XXX'},
    completed: {type: Boolean, default: false},
    note: {type: String, default:'deim1', enum : ['deim1', 'deim2', 'deim3']},
    updated_at: {type: Date, default: Date.now}
});


module.exports = mongoose.model('Todo', TodoSchema);

