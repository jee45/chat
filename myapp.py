import base64
import uuid

import flask
#import flask.ext.socketio

import flask_socketio








app = flask.Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'bollocks!'
io =   flask_socketio.SocketIO(app)
urlkeys = {}
rooms={}


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
    urlkeys [keyFromUrl]= topic

    # go to the url
    return flask.redirect('/'+keyFromUrl)



@app.route('/<keyFromUrl>')
def back(keyFromUrl):

    sid = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

    sid= 'user'+sid
    flask.session['sid'] = sid
    flask.session['room']  = keyFromUrl


    print( flask.session['room'] )

    print("urlkeys ****** ",urlkeys)
    #get the topic from the key
    if keyFromUrl in urlkeys.keys():
        topic =  urlkeys [keyFromUrl]

    else:
        topic =  urlkeys[keyFromUrl] = "no room was created for this yet"

    return flask.render_template('back.html', urlKey=keyFromUrl , sid = sid, topic=topic)








@io.on('connect' )
def connect():

    print("connecting you to the users in the room: ", flask.session['room'])
    print('connected')
    sid = flask.session['sid']
    name = ''
    if 'name' in flask.session:
        name = flask.session['name']

    flask_socketio.join_room(flask.session['sid'])
    io.emit("connect", { 'sid': sid, 'room': flask.session['room'], 'name':name } , room=flask.session['sid'])



@io.on('enterchat' )
def enterchat(data):



    print('entering chat')
    # data:
    # name, roomid, sid

    sid = flask_socketio.rooms()
    print('........ ',sid[0])
    print('........ ',flask_socketio.rooms())


    flask.session['name'] = data['name']





    if flask.session['room'] not in flask_socketio.rooms():
        flask_socketio.join_room(flask.session['room'])


        if flask.session['room'] in rooms:
            rooms[ flask.session['room']].append(flask.session['name'])
        else:
            rooms[ flask.session['room']] = flask.session['name']


        print("............", rooms)


        #get all the users in this room .
        #for each user in this room,
        print('sid: ',flask.session['sid'])
        for each in rooms[ flask.session['room']]:

            if each != flask.session['name']:
                io.emit("user-joined", { "name": each} , room=flask.session['sid'])

            # emit a user joined to only me.

        io.emit("joined", { "name": each} , room=flask.session['sid'])

        # for eachuser in theRoom:
        #     io.emit("user-joined", { "name": data['name']} , room=flask.session['sid'] )


        #send to everyone in the room
        io.emit("user-joined", { "name": data['name']}, room=flask.session['room'], broadcast=False )







@io.on('chat')
def chat(data):


    #print("lkasdf", flask.request.args)
    print("chat data",data)


    sender = flask.session['name']
    room = flask.session['room']
    message = data['message']

    print('++++ ',room)


    io.emit("new-chat",  { 'sender': sender, 'message': message } , room=room )





if __name__ == '__main__':
    io.run(app)
