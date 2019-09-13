
# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request
import git

app = Flask(__name__)

@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        print("Before Path")
        repo = git.Repo('./xamarinweatherservice')
        origin = repo.remotes.origin
        print("Before Pull")
        origin.pull()
        print("After Pull")
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

@app.route('/')
def hello_world():
    return 'Hello from Flask!'
