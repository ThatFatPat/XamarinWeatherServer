from flask import Flask, request
import hashlib
import hmac
import git
import os
import logging

def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

def handle_pull():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    logging.error(WEBHOOK_SECRET)
    GIT_FOLDER = "/home/ThatFatPat/xamarinweatherservice"
    logging.error("defined folder")
    if not is_valid_signature(x_hub_signature, request.data, WEBHOOK_SECRET):
        logging.error("wrong key")
        return 'Invalid signature', 403
    if request.method == 'POST':
        logging.error("in if")
        repo = git.Repo(GIT_FOLDER)
        logging.error("found repo")
        origin = repo.remotes.origin
        origin.pull()
        logging.error("past pull")
        return 'Updated PythonAnywhere successfully', 200
    else:
        logging.error("400")
        return 'Wrong event type', 400
    logging.error("WAT")