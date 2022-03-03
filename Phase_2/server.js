//Design Reference
//https://app.diagrams.net/#G1D0nWAEBz9R4ezVkePmG-yefGfC8cGWi9

//Environment Variables set up by Docker compose
const port  = process.env.Port;
const uri = process.env.DB_connect.toString();
const database_name = process.env.db_name.toString();
const app_name = process.env.app_name.toString();
var chat_counter = 0;
const host = process.env.host
//onst lead = process.env.lead
const rainbow_bridge = process.env.rainbow_bridge

//Middleware
const express = require("express");
const socketIO = require("socket.io")
const socket_client = require("socket.io-client");
var assert = require('assert');
const http = require("http")
const app = express();
const MongoClient = require('mongodb').MongoClient;

//client
const c_server = http.createServer(app);
const c_io = socketIO(c_server);

//node
const n_io_client;

const n_server =  http.createServer(app); 
const n_io_server = socketIO(http);

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
app.use('/phase_1.css', express.static(__dirname + '/phase_1.css'));
app.get("/phase_2", (req, res) => res.sendFile(__dirname + "/index.html"));

//Leader Node
if(host == app_name){
  //web client
  c_io.on("connection", function(socket) {
    
    //initial connection
    console.log("User Connected")
    c_io.emit('greetings',JSON.stringify("Greetings from: "+app_name))
    c_io.emit('chat_history', JSON.stringify(chat_history,replacer));
    
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
      c_io.emit('chat_history', JSON.stringify(chat_history,replacer));
      });


  });

  c_server.listen(port, () => console.log("listening on http://localhost:"+port));
  
  //node server
  n_io_server.on("connection",function(socket){
    n_io_server.emit('server_to_server');
    console.log("new node has joined");
    
    socket.on("heiarchy", function(msg){
      console.log("delegations")
    });
  });

  n_server.listen(rainbow_bridge,host,() => console.log("Leader listening on http://"+host+":"+rainbow_bridge));
}

//Follower Node
else {
  //node client
  n_io_client = socket_client.connect("http://"+host+":"+rainbow_bridge,{reconnect:true});
  n_io_client.emit('new node has joined');
  console.log("new node has joined");
  
  n_io_client.on("connect",function(){
  }); 

  n_io_client.on("server_to_server", function(msg){
    console.log("server to server babyyyyyyyy")
  });
}

function check_data(){
  //Check database's chathistory and make sure we're updated
  
}

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
