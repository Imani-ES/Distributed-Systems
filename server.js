const express = require("express");
const app = express();
const http = require("http")
var server = http.createServer(app);
const socketIO = require("socket.io")
var io = socketIO(server);
const port  = process.env.Port || 3000;

//database init
const { MongoClient } = require("mongodb");
const { WSATYPE_NOT_FOUND } = require('constants');
const imani_dbPass = process.env.DB_PASS_442;
const imani_uri = 'mongodb+srv://CSE442:' + 'CSE442cse' + '@cluster0.k7tia.mongodb.net/test';
const imani_client = new MongoClient(imani_uri,{keepAlive: 1});


if(get_room_info()){
    console.log("Got room data");
}

app.use('/movie_room.css', express.static(__dirname + '/movie_room.css'));
app.get("/movie_room", (req, res) => res.sendFile(__dirname + "/movie_room.html"));

 io.on("connection", function(socket) {
  io.emit("user connected",JSON.stringify("Hello via Json",replacer));

  socket.on("client", function(msg) {
    console.log("hello from client"+msg);    
  });

  socket.on("chat", function(msg){
    console.log("Processing chat from User: " + msg);
    chat_history.push(["User x",msg]);
    //find a way to push to database collection
    io.emit('chat_history', JSON.stringify(chat_history,replacer));
  });


 });

 server.listen(port, () => console.log("listening on http://localhost:"+port));

 
async function get_room_info() {
  //Movie Data stored as
/* movie_name: "moviename"
  genre:""
  yeae:""
  img_url:""
*/ 
await imani_client.connect();
console.log("MongoDB connected");
const db = imani_client.db("Movies");
const movies = db.collection('MovieData');

movies.findOne({room_info:room_name},{}, function(err, result) {
  if (err) throw err;
   return  (1);
}); 
return 0;
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