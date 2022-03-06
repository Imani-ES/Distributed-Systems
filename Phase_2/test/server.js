//Design Reference
//https://app.diagrams.net/#G1D0nWAEBz9R4ezVkePmG-yefGfC8cGWi9

//Environment Variables set up by Docker compose
  const Client_Port  = process.env.Client_Port;
  const uri = process.env.DB_connect.toString();
  const uri_2 = process.env.DB_connect_2.toString();
  const uri_3 = process.env.DB_connect_3.toString();
  const database_name = process.env.db_name.toString();
  const app_name = process.env.app_name.toString();
  var chat_counter = 0;
  const host = process.env.host
  const Node_Port = process.env.Node_Port;

//Middleware
  const express = require("express");
  const socketIO = require("socket.io")
  var assert = require('assert');
  const http = require("http")
  const app = express();
  const MongoClient = require('mongodb').MongoClient;

//leader -> client
  const c_server = http.createServer(app);
  const c_io = socketIO(c_server);

//leader -> node
  const n_server =  http.createServer(app); 
  const n_io = socketIO(n_server);

//node -> leader
  const n_io_c = require("socket.io-client");;

//Database 1
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

//Database
MongoClient.connect(uri_2, function(err, db) {
  if (err) throw err;
  console.log("Mongo 2 Connected");
  _db = db.db("test");
  var chat_history = {id: chat_counter,chat_history:['Welcome all']};
  _db.collection("chat_collection").insertOne(chat_history, function(err, res){
    if (err) throw err;
    console.log("Collection created!");
    console.log("History element instantiated");
  })
 chat_counter += 1;
});

//Create Database
MongoClient.connect(uri_3, function(err, db) {
  if (err) throw err;
  console.log("Mongo 3 Connected");
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
  //node server
  n_io.on("connection",function(socket){
    //greetings
    console.log("Server Client Connected")
    n_io.emit('server_to_server',app_name);
    socket.on("server_to_server", function(msg){
      console.log("Welcome "+msg)
    });
        
    //communicate while running
    socket.on("double_check_chat_response", function(msg){
      console.log(msg[0]+"proccessed: "+msg[1]);
    });

  });
  n_server.listen(Node_Port,host,() => console.log("Leader listening on http://"+host+":"+Node_Port));

  //web client
  c_io.on("connection", function(socket) {  
    //initial connection
    console.log("User Connected")
    c_io.emit('greetings',JSON.stringify("Greetings from: "+app_name))
    c_io.emit('chat_history', JSON.stringify(chat_history,replacer));
    
    //messages
    socket.on("chat", function(msg){
      //send to other nodes
      console.log("Sending req to othe nodes");
      n_io_server.emit("double_check_chat",msg);

      //process chat
      var ret = process_message(msg);

      //send chat history to client
      c_io.emit('chat_history', JSON.stringify(ret,replacer));
      });
  });
  c_server.listen(Client_Port, () => console.log("listening on http://localhost:"+Client_Port));
  }
//Follower Node
else {
  //node client
  console.log("Attempting to connect to Leader @ "+"http://"+host+":"+Node_Port);
  n_io_client = n_io_c("http://"+host+":"+Node_Port);
  //n_io_client.connect("http://"+host+":"+rainbow_bridge);
  
  console.log(app_name + " following "+host);
  n_io_client.emit('server_to_server',app_name);
  
  n_io_client.on("double_check_chat",function(msg){
    //process chat
    console.log("Recieved Double check prompt");
    var ret = process_message(msg);

    n_io_client.emit('double_check_chat_response',[app_name,ret]);
  }); 

  n_io_client.on("server_to_server", function(msg){
    console.log("server to server baby, Hi "+msg)
  });
  
  
}

function check_data(){
  //Check database's chathistory and make sure we're updated
  
}

//all nodes do this
function process_message(msg){
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
  return chat_history;
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
