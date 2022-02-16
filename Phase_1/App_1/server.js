const express = require("express");
const app = express();
const http = require("http")
var server = http.createServer(app);
const socketIO = require("socket.io")
var io = socketIO(server);

//process.env.Port will be passed to the docker container 
const port  = process.env.Port || 3000;
const DB_Name = process.env.DB_Name;
const DB_Port = process.env.DB_Port;

//database init
const database = 'mongodb://mongodb:27017';
const client = new MongoClient(uri,{keepAlive: 1});

chat_history = ['Welcome all'];
/*
if(get_chat_history()){
    console.log("Got room data");
}
*/
app.use('/phase_1.css', express.static(__dirname + '/phase_1.css'));
app.get("/phase_1", (req, res) => res.sendFile(__dirname + "/index.html"));

 io.on("connection", function(socket) {
  io.emit('chat_history', JSON.stringify(chat_history,replacer));

  socket.on("chat", function(msg){
    console.log("Processing chat from User: " + msg);
    chat_history.push(msg);
    //find a way to push to database collection
    io.emit('chat_history', JSON.stringify(chat_history,replacer));
  });


 });

 server.listen(port, () => console.log("listening on http://localhost:"+port));

/*
async function get_chat_history() {
await client.connect();
console.log("MongoDB connected");
const db = client.db("dbname");
const chat = db.collection('collectionname');

chat.findOne({room_info:room_name},{}, function(err, result) {
  if (err) throw err;
   return  (1);
}); 
return 0;
}
*/

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