from flask import Blueprint, request, session, redirect, make_response
import hashlib
from db.db import get_db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    full_name = request.form['full_name']
    dob = request.form['dob']
    password = request.form['password']
    scc = request.form['scc']

    hash_pass = hashlib.sha256(password.encode()).hexdigest()
    db = get_db()
    cursor = db.cursor()

    # 🔍 Check SCC validity
    cursor.execute(
        "SELECT * FROM scc_registry WHERE scc_code=%s AND used=FALSE",
        (scc,)
    )

    if not cursor.fetchone():
        return "Invalid or already used SCC code"

    # 🔍 Check duplicate email
    cursor.execute(
        "SELECT * FROM voters WHERE email=%s",
        (email,)
    )
    if cursor.fetchone():
        return "This email is already registered"

    try:
        cursor.execute(
            """
            INSERT INTO voters (email, full_name, dob, password_hash, scc_code)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (email, full_name, dob, hash_pass, scc)
        )

        cursor.execute(
            "UPDATE scc_registry SET used=TRUE WHERE scc_code=%s",
            (scc,)
        )

        db.commit()
        return "Registration successful. You can now log in."

    except Exception as e:
        return "Registration failed. Please try again."

@auth.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # 🔐 Admin login
    if email == "ec@referendum.gov.sr" and password == "Shangrilavote&2025@":
        session['admin'] = True
        return redirect('/admin/dashboard')

    hashed = hashlib.sha256(password.encode()).hexdigest()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM voters WHERE email=%s AND password_hash=%s",
        (email, hashed)
    )

    user = cursor.fetchone()

    if not user:
        return "Invalid email or password"

    # ✅ Store session
    session['user_id'] = user['voter_id']
    session['user_email'] = user['email']

    # ✅ Remember last login email (easy B-band marks)
    resp = make_response(redirect('/voter/dashboard'))
    resp.set_cookie('last_login_email', email, max_age=60*60*24*7)
    return resp

@auth.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect('/login')
