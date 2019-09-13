
# A very simple Bottle Hello World app for you to get started with...
from bottle import default_app, route, request
import git


@route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('./xamarinweatherserver')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

@route('/')
def hello_world():
    return 'Hello from Bottle!'

application = default_app()
