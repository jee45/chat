
import base64
import uuid

import flask
#import flask.ext.socketio

import flask_socketio

#flask_socketio.emit() # to the current connection
#io.emit() #broadcast

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







@app.route('/submitNewChat', methods=['POST'])
def submitNewChat():

    # get the topic in the form
    topic = flask.request.form['topic']



    # create a url hash from the submitted topic
    keyFromUrl = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

    # add denote this key is a room url
    keyFromUrl = "room"+keyFromUrl


    # store the hurl hash as the key, and the topic as the value in the rooms dict
    urlkeys[keyFromUrl]= topic

    print(urlkeys)

    # go to the url
    return flask.redirect('/'+keyFromUrl)


@app.route('/<keyFromUrl>')
def back(keyFromUrl):

    # if the user is at this page,
    # they have either created a room
    # or been sent the url.


    #if the room is not yet in the list
    if keyFromUrl not in rooms:
        rooms[keyFromUrl] = []




    #if the key has a topic
    if keyFromUrl in urlkeys.keys():


        #store the room in session
        flask.session['room']  = keyFromUrl

        # get the topic for the url
        topic =  urlkeys [keyFromUrl]

        # create a session or socket id for the user
        sid = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

        # denote it is a user key
        sid= 'user' + sid

        # store the user id in session
        flask.session['sid'] = sid


        #send them on thier way
        return flask.render_template('back.html', urlKey=keyFromUrl , sid = sid, topic=topic)

    else:
        flask.flash('url not in the keys dict.')

        flask.flash('no sids issued, no room stored in session. ')
        return flask.redirect('/')















@io.on('connect' )
def connect():

    print('socektid # ', flask_socketio.rooms(), 'connecting in  io: .... ')

    # if they are connected,
    socketId =  flask_socketio.rooms()

    print(socketId)

    # how to send to just them?
    io.emit('connect',  room = socketId[0] )

    print('emitting to connect so user can just rejoin the room')
    print('user is in the  rooms: ', flask_socketio.rooms())



@io.on('enterchat' )
def enterchat(data):

    flask.session['name'] = data['name']


    print('entering chat  in io: .... ')
    print(data)

    print('data sid :', data['sid'])
    print('sess sid :', flask.session['sid'])

    print('data room :', data['room'])
    print('sess room :', flask.session['room'])

    print('data name :', data['name'])
    print('sess name :', flask.session['name'])

    # >>>> >>>> >>>> >>>> >>>> >>>> >>>> >>>>
    # >>>> >>>> >>>> >>>> >>>> >>>> >>>> >>>>

    # if the room sent is already in thier flask_socketio.rooms()
    if data['room'] in flask_socketio.rooms():
        #do nothing
        print('already in the room. ')


    #else
    else:



        # they join the room
        flask_socketio.join_room(data['room'])
        flask_socketio.join_room(data['sid'])

        #emit that they have joined.
        print("trying to send a message to my room: " , flask.session['sid'] )
        print("is this room the list of rooms im in? : " , flask_socketio.rooms() )

        io.emit("joined", { "name": data['name']} , room=flask.session['sid'] )


        # if they are already in the list of users in the  room array.
        print('listing rooms: ' , rooms)
        print('is the room sent one of them? : ' , data['room'])

        print(data)

        #if the room exists
        if data['room'] in rooms:
            #if the user is already in the room
            if data['name'] in rooms[data['room']]:
                #do nothing?
                print( )
                print('the user:',  data['name'])
                print('is in the room:',  rooms[data['room']])


            # else
            else:

                # add me to the list of users in the rooms array
                rooms[data['room']].append(data['name'])
                print('rooms list: ', rooms)




                # get the names of the others already there.
                # send it to only them
                for name in rooms[data['room']]:
                    if name != data['name']:
                        io.emit("user-joined", { "name": name}, room=data['sid']  )


                # notify the room that i have joined
                io.emit("user-joined", { "name": data['name']}, room=data['room']  )

        else:
            print('the room doesnt exist')

            # is there something to do id the room doesnt exist yet?
            # create it in the list ?
            # add this user to the list ?

            rooms[data['room']] = [data['name']]

            print('rooms list: ', rooms)


            # notify the room that they have joined
            io.emit("user-joined", { "name": data['name']}, room=data['room']  )















    # <<<< <<<< <<<< <<<< <<<< <<<< <<<< <<<<
    # <<<< <<<< <<<< <<<< <<<< <<<< <<<< <<<<

@io.on('chat')
def chat(data):
    print('submitting new chat  in io: .... ')


    #print("lkasdf", flask.request.args)
    print("chat data",data)


    sender = flask.session['name']
    room = flask.session['room']
    message = data['message']

    print('++++ ',room)
    print('is it one of these?', flask_socketio.rooms())
    io.emit("new-chat",  { 'sender': sender, 'message': message } , room=room )





if __name__ == '__main__':
    io.run(app)
