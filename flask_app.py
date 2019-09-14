from flask import Flask, request, jsonify
from socket import gethostname
import os
import xamarinweather_db as db
import github_webhook
import json

app = Flask(__name__)

def processRequest(func, request):
    try:
        data = request.get_json()
        user = data.get("username", None)
        password = data.get("password", None)
        if user is None or password is None:
            return '', 400
        city = data.get("city", None)
        if city is None:
            resp = func(user, password)
        else:
            resp = func(user, password, city)
        return jsonify(resp.data), resp.resp_code
    except Exception as e:
        return '', 400

@app.route('/update_server', methods=['POST'])
def webhook():
    github_webhook.handle_pull()

@app.route('/getCities', methods=['POST'])
def getCities():
    return processRequest(db.getCitiesForUser, request)

@app.route('/addCity', methods=['POST'])
def addCity():
    return processRequest(db.addCityForUser, request)

@app.route('/checkCredentials', methods=['POST'])
def checkCredentials():
    return processRequest(db.checkCredentials, request)

@app.route('/registerUser', methods=['POST'])
def registerUser():
    return processRequest(db.registerUser, request)


if __name__ == "__main__":
    db.init_db()
    if 'liveconsole' not in gethostname() and os.getenv('VSCODE') != "1":
        app.run(ssl_context='adhoc')