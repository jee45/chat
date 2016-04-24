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




    flask.session['room']  = keyFromUrl

    print(
    flask.session['room'] )

    #get the topic from the key
    if keyFromUrl in rooms.keys():
        topic =  rooms [keyFromUrl]

    else:
        topic =  rooms [keyFromUrl] = "no room was created for this yet"

    return flask.render_template('back.html', urlKey=keyFromUrl , topic=topic)








@io.on('connect' )
def connect():

    print("connecting you to the users in the room: ", flask.session['room'])
    print('connected')








@io.on('enterchat' )
def enterchat(data):



    # data:
    # name, roomid, sid

    flask.session['sid'] = data['sid']
    flask.session['name'] = data['name']


    flask.session['room']  = data['room']



    if flask.session['room'] not in  flask_socketio.rooms():
        flask_socketio.join_room(flask.session['room'])


        #send to the user who just joined
        io.emit("joined", { "name": data["name"]} )

        # for eachuser in theRoom:
        #     io.emit("user-joined", { "name": data['name']} , room=flask.session['sid'] )


        #send to everyone in the room
        io.emit("user-joined", { "name": data['name']}  )







@io.on('chat')
def chat(data):


    #print("lkasdf", flask.request.args)
    print("chat data",data)


    sender = flask.session['name']
    room= flask.session['name']
    message = data['message']


    io.emit("new-chat",  { 'sender': sender, 'message': message }  )





if __name__ == '__main__':
    io.run(app)
