var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var uri = 'mongodb://root:rootpwd@localhost:27017';
console.log("Running test connection for"+ uri );
MongoClient.connect(uri, function(err, db) {
   assert.equal(null, err);
   console.log("Mongo Connected");
   _db = db.db("test");
   _db.createCollection("chat_collection", function(err, res) {
      assert.equal(null, err);
     console.log("Collection created!");
   });
   var chat_history = {chat_history:['Welcome all']};
   _db.collection("chat_collection").insertOne(chat_history, function(err, res){
      assert.equal(null, err);
     console.log("History element instantiated");
   })
   //db.close();
   console.log("Mongo Connection closed");
 });