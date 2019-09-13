from flask import Flask, request
from socket import gethostname
import os
import xamarinweather_db as db
import github_webhook

#region Constants
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
DB_PATH = "./xamarinweatherdb.db"
#endregion

app = Flask(__name__)

@app.route('/update_server', methods=['POST'])
def webhook():
    github_webhook.handle_pull()

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

if __name__ == "__main__":
    db.init_db(DB_PATH)
    if 'liveconsole' not in gethostname() and os.getenv('VSCODE') != "1":
        app.run()