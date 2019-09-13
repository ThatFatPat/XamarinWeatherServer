
# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request
import git
import hmac
import hashlib
import os

WEBHOOK_SECRET = os.getenv("SECRET_KEY")
app = Flask(__name__)


def is_valid_signature(x_hub_signature, data, private_key):
    # x_hub_signature and data are from the webhook payload
    # private key is your webhook secret
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

@app.route('/update_server', methods=['POST'])
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if not is_valid_signature(x_hub_signature, request.data, WEBHOOK_SECRET):
        return 'Invalid signature', 403
    if request.method == 'POST':
        repo = git.Repo('./xamarinweatherservice')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

@app.route('/')
def hello_world():
    return 'Hello from Flask!'