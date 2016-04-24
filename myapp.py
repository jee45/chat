import base64
import uuid

import flask
#import flask.ext.socketio
import flask_socketio

app = flask.Flask(__name__)
app.debug = True

app.config['SECRET_KEY'] = 'bollocks!'

io =   flask_socketio.SocketIO(app)

rooms = {}
names={}

users=[]

@app.route('/')
def index():
    #go to the front page.
	return flask.render_template('front.html')




@app.route('/new-chat', methods=['POST'])
def newchat():

    # get the topic in the form
    topic = flask.request.form['topic']



    # create a url hash from the topic
    keyFromUrl = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

    # store the hurl hash as the key, and the topic as the value in the rooms dict
    keyFromUrl = "room"+keyFromUrl
    rooms [keyFromUrl]= topic




    # go to the url
    return flask.redirect('/'+keyFromUrl)



@app.route('/<keyFromUrl>')
def back(keyFromUrl):


    #
    # # if the user is already have a session,
    # if flask.session['sid']:
    #
    #     #session id is the value in the session.
    #     sessionId = flask.session['sid']
    #
    # else: #otherwize
    #     # create one, and make it a session id
    #     sessionId = flask.session['sid'] =  base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

    sessionId = flask.session['sid'] =  "user"+base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')
    print (sessionId)

    #get the topic from the key
    if keyFromUrl in rooms.keys():
        topic =  rooms [keyFromUrl]
    else:
        topic =  rooms [keyFromUrl] = "no room was created for this yet"

    return flask.render_template('back.html', urlKey=keyFromUrl, sessionId =sessionId, topic=topic)




clients = []


@io.on('connect' )
def connect():


    #this will mean that the 2nd page is loaded.
    print("namespace" )
    print("rooms", flask_socketio.rooms() )

    print(rooms)


    print('connected')








@io.on('enterchat' )
def enterchat(data):



    # data:
    # name, roomid, sid
    print('enter session : ' , end='')
    print(data)



    # if the user doesnt have a session id yet,
    if 'sid' not in flask.session :
        # give them a new  one
        print('new session')
        flask.session['sid'] =  "user"+base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')
    else:
        print('already in session')


    names[flask.session['sid']] = data['name']
    print(names)


    #if the room exists,
    if data['room'] in rooms:
        # join it
        print(data['room'])

        if data['room'] not in flask_socketio.rooms():

            flask_socketio.join_room(data['room'])
        else:
            print('.................... youre already in this room' )


    else: # otherwise

        # join the trash room
        flask_socketio.join_room('room not found')


    #send to the user who just joined
    io.emit("joined", { "name": data["name"]})


    #send to everyone in the room
    io.emit("user-joined", { "name": data['name']}, room=data['room']  )


    print("rooms", flask_socketio.rooms() )
    print(rooms)





@io.on('chat')
def chat(data):



    print("chat data",data)

    sender = names[data['sid']]
    room= data['room']
    message = data['message']

    io.emit("new-chat",  { 'sender': sender, 'message': message } , room=room )



if __name__ == '__main__':
    io.run(app)
