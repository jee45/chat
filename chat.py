import flask

app = flask.Flask(__name__)
app.cofig.from_pyfile('settings.py')


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
