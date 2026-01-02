from flask import Flask, render_template, session
from flask_session import Session
from db.db import get_db
from auth.auth import auth
from voter.voter import voter
from admin.admin import admin
from api.api import api

app = Flask(__name__)

# 🔐 Session configuration
app.secret_key = "mslr_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def home():
    return "MSLR is running!"

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')
  
app.register_blueprint(auth)
app.register_blueprint(voter)
app.register_blueprint(admin)
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)
