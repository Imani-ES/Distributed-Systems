var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var url = 'mongodb://root:rootpwd@localhost:27017';
console.log("Running test connection for"+ url );
MongoClient.connect(url, function(err, db) {
   assert.equal(null, err);
   console.log("Test Passed");
   db.close();
});