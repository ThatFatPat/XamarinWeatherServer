from flask import Flask, request
import hashlib
import hmac
import git
import os

#region Constants
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
GIT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/xamarinweatherservice")
#endregion

def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

def handle_pull():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if not is_valid_signature(x_hub_signature, request.data, WEBHOOK_SECRET):
        return 'Invalid signature', 403
    if request.method == 'POST':
        repo = git.Repo(GIT_FOLDER)
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400