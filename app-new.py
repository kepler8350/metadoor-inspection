import os
from flask import Flask, request, session, redirect, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'metadoor-key-2024'
DB_PATH = '/tmp/metadoor.db'

@app.route('/mobile-new')
def mobile_new():
    with open('/mnt/user-data/outputs/metadoor-mobile-app.html', 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
