import base64
import uuid

import flask
#import flask.ext.socketio as io
import flask_socketio

app = flask.Flask(__name__)
app.debug = True

app.config['SECRET_KEY'] = 'bollocks!'

io =   flask_socketio.SocketIO(app)

rooms = {}
names={}

@app.route('/')
def index():
	return flask.render_template('front.html')


@app.route('/new-chat', methods=['POST'])
def newchat():

    #this is where we do the url shortener thing

    topic = flask.request.form['topic']



    #create
    #  keyFromUrl = url hash thing
    #keyFromUrl = 'keyFromUrl'
    keyFromUrl = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')
    rooms [keyFromUrl]= topic




    #flask.session['auth__id'] = sid
    flask.session['sid'] =  base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

    return flask.redirect('/'+keyFromUrl)



@app.route('/<keyFromUrl>')
def back(keyFromUrl):

    sessionId = flask.session['sid']

    # if the user is doesnt already have a session,

    if not flask.session['sid']:
        flask.session['sid'] =  base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')


    topic =  rooms [keyFromUrl]

    return flask.render_template('back.html', urlKey=keyFromUrl, sessionId =sessionId, topic=topic)





@io.on('connect' )
def connect():
    #this will mean that the 2nd page is loaded.


    print('connected')






@io.on('enterchat' )
def enterchat(data):

    # data:
    # name, roomid, sid
    print('enter session')
    print(data)

    # if the user is doesnt already have a session,
    '''
    if data['name'] not in names.keys():
        # give them one
        names[flask.session['sid']] = data['name']
    '''
    names[flask.session['sid']] = data['name']


    if rooms[data['room']]:
        flask_socketio.join_room(rooms[data['room']])

    else:
        flask_socketio.join_room('room not found')


    #send to the user who just joined
    io.emit("joined", { "name": data["name"]} )


    #send to everyone in the room
    io.emit("user-joined", { "name": data['name']  } )




@io.on('chat' )
def chat(data):

    sender = names[data['sid']]
    message = data['message']
    io.emit("new-chat",  { 'sender': sender, 'message': message } )



if __name__ == '__main__':
    io.run(app)
