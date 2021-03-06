const express = require("express");
var assert = require('assert');
const app = express();
const http = require("http")
const MongoClient = require('mongodb').MongoClient;
var server = http.createServer(app);
const socketIO = require("socket.io")
var io = socketIO(server);

//Environment Variables set up by Docker compose
const port  = process.env.Port;
const uri = process.env.DB_connect.toString();
const database_name = process.env.db_name.toString();
const app_name = process.env.app_name.toString();
var chat_counter = 0;
//Create Database
MongoClient.connect(uri, function(err, db) {
  if (err) throw err;
  console.log("Mongo Connected");
  _db = db.db("test");
  var chat_history = {id: chat_counter,chat_history:['Welcome all']};
  _db.collection("chat_collection").insertOne(chat_history, function(err, res){
    if (err) throw err;
    console.log("Collection created!");
    console.log("History element instantiated");
  })
 chat_counter += 1;
});

  //global variables
  chat_history = ['Welcome all'];
  db = {}

  //files used
  app.use('/phase_1.css', express.static(__dirname + '/phase_1.css'));

  //send client HTML file
  app.get("/phase_1", (req, res) => res.sendFile(__dirname + "/index.html"));

  //socket functionality
  io.on("connection", function(socket) {
    
    //initial connection
    console.log("User Connected")
    io.emit('chat_history', JSON.stringify(chat_history,replacer));
    
    //messages
    socket.on("chat", function(msg){

      console.log("Processing chat: " + msg);
      chat_history.push(msg);

      //database connect
      console.log("Conecting to mongo");
      MongoClient.connect(uri, function(err, _db) {
        assert.equal(null, err);
        console.log("Connected to mongo");
        var db = _db.db(database_name)
        var chat_history = {id:chat_counter,chat_history:chat_history};
        db.collection("chat_collection").insertOne(chat_history, function(err, res){
          assert.equal(null, err);
          console.log(chat_history+" logged");
        });
        chat_counter += 1;
      });
      io.emit('chat_history', JSON.stringify(chat_history,replacer));
      });


  });

//JSON wrapper & unwrapper functions
function replacer(key, value) {
  if(value instanceof Map) {
    return {
      dataType: 'Map',
      value: Array.from(value.entries()), // or with spread: value: [...value]
    };
  } else {
    return value;
  }
}
function reviver(key, value) {
  if(typeof value === 'object' && value !== null) {
    if (value.dataType === 'Map') {
      return new Map(value.value);
    }
  }
  return value;
}
server.listen(port, () => console.log("listening on http://localhost:"+port));
