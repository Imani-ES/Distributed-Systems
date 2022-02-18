const express = require("express");
const app = express();
const http = require("http")
const MongoClient = require('mongodb').MongoClient;
var server = http.createServer(app);
const socketIO = require("socket.io")
var io = socketIO(server);

//Environment Variables set up by Docker compose
const port  = process.env.Port || 3000;

//database stuff
const uri = process.env.DB_connect || "mongodb://root:rootpwd@127.0.0.1:27017";
console.log("Database Uri: " + uri);
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
     MongoClient.connect(uri,{ useNewUrlParser: true})
     /*
      function(err,_db){
      useUnifiedTopology: true,
     
       if (err) throw err;
       db = _db;
       console.log("Connected to Mongo!!");
     })
     */
     //response
     io.emit('chat_history', JSON.stringify(chat_history,replacer));
    });


 });

// async function get_chat_history() {
// await client.connect();
// console.log("MongoDB connected");
// const db = client.db("dbname");
// const chat = db.collection('collectionname');

// chat.findOne({room_info:room_name},{}, function(err, result) {
//   if (err) throw err;
//   return  (1);
// }); 
// return 1;
// }


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
