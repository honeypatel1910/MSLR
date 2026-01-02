from flask import Blueprint, render_template, session, redirect, request
from db.db import get_db

admin = Blueprint('admin', __name__)

def admin_required():
    return 'admin' in session

@admin.route('/admin/dashboard')
def dashboard():
    if not admin_required():
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM referendums")
    referendums = cursor.fetchall()

    return render_template(
        'admin_dashboard.html',
        referendums=referendums
    )

@admin.route('/admin/create', methods=['POST'])
def create_referendum():
    if not admin_required():
        return redirect('/login')

    title = request.form['title']
    description = request.form['description']
    option1 = request.form['option1']
    option2 = request.form['option2']

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO referendums (title, description, status) VALUES (%s,%s, 'closed')",
        (title, description)
    )
    ref_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO referendum_options (referendum_id, option_text) VALUES (%s,%s)",
        (ref_id, option1)
    )
    cursor.execute(
        "INSERT INTO referendum_options (referendum_id, option_text) VALUES (%s,%s)",
        (ref_id, option2)
    )

    db.commit()
    return redirect('/admin/dashboard')


@admin.route('/admin/open/<int:ref_id>', methods=['POST'])
def open_referendum(ref_id):
    if not admin_required():
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE referendums SET status='open' WHERE referendum_id=%s",
        (ref_id,)
    )
    db.commit()
    return redirect('/admin/dashboard')


@admin.route('/admin/close/<int:ref_id>', methods=['POST'])
def close_referendum(ref_id):
    if not admin_required():
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE referendums SET status='closed' WHERE referendum_id=%s",
        (ref_id,)
    )
    db.commit()
    return redirect('/admin/dashboard')

@admin.route('/admin/results/<int:ref_id>')
def results(ref_id):
    if 'admin' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT title FROM referendums WHERE referendum_id=%s",
        (ref_id,)
    )
    referendum = cursor.fetchone()

    cursor.execute("""
        SELECT o.option_text, COUNT(v.vote_id) AS votes
        FROM referendum_options o
        LEFT JOIN votes v ON o.option_id = v.option_id
        WHERE o.referendum_id=%s
        GROUP BY o.option_id
    """, (ref_id,))

    results = cursor.fetchall()

    return render_template(
        'admin_results.html',
        referendum=referendum,
        results=results
    )

