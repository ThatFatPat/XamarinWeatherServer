
# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request
from socket import gethostname
import git
import hmac
import hashlib
import sqlite3
import os

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
DB_PATH = "./xamarinweatherdb.db"
app = Flask(__name__)

def init_db(path):
    conn = sqlite3.connect(DB_PATH)  # You can create a new database by changing the name within the quotes
    c = conn.cursor() # The database will be saved in the location where your 'py' file is saved
    c.execute('''CREATE TABLE IF NOT EXISTS "Cities" (
                "CityId"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "LocationId"	TEXT NOT NULL,
                "Lat"	NUMERIC NOT NULL,
                "Lon"	NUMERIC NOT NULL
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS "UsernamesCities" (
                "UserId"	INTEGER NOT NULL,
                "CityId"	TEXT NOT NULL,
                FOREIGN KEY("UserId") REFERENCES "Users"("UserId"),
                FOREIGN KEY("CityId") REFERENCES "Cities"("CityId")
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS "Users" (
                "UserId"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "Username"	TEXT NOT NULL
            )''')
                                
    conn.commit()

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

if __name__ == "__main__":
    init_db(DB_PATH)
    if 'liveconsole' not in gethostname() and os.getenv('VSCODE') != "1":
        app.run()