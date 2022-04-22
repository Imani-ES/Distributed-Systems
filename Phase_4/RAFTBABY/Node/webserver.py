#Src: https://flask-socketio.readthedocs.io/en/latest/getting_started.html#initialization
# https://medium.com/@abhishekchaudhary_28536/building-apps-using-flask-socketio-and-javascript-socket-io-part-1-ae448768643
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send

# Creating a flask app and using it to instantiate a socket object
app = Flask(__name__)
socketio = SocketIO(app)


# Handler for default flask route
@app.route('/')
def index():
    return render_template('index.html')
# Handler for a message recieved over 'connect' channel
@socketio.on('connect')
def test_connect():
    send('greetings',{'data':"Greetings from: "+name})
    send('chat_history',{'data':chat_history})
@socketio.on('chat')
def handle_chat(chat):
    send(chat, namespace='/chat')
    #AppendRPC w chat history to followers
    #send chat history back to clients
    send('chat_history',{'data':chat_history})


# Notice how socketio.run takes care of app instantiation as well.
def run_client(host,port,socketio,app):
    socketio.run(app, host=host,port = port)

def kill_client(socketio):
    socketio.disconnect()