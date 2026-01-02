from flask import Blueprint, render_template, session, redirect, request
from db.db import get_db

voter = Blueprint('voter', __name__)

@voter.route('/voter/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    voter_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM referendums WHERE status='open'")
    referendums = cursor.fetchall()

    for ref in referendums:
        cursor.execute(
            "SELECT * FROM referendum_options WHERE referendum_id=%s",
            (ref['referendum_id'],)
        )
        ref['options'] = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM votes WHERE voter_id=%s AND referendum_id=%s",
            (voter_id, ref['referendum_id'])
        )
        ref['has_voted'] = cursor.fetchone() is not None

    return render_template(
        'voter_dashboard.html',
        referendums=referendums
    )

@voter.route('/vote', methods=['POST'])
def vote():
    if 'user_id' not in session:
        return redirect('/login')

    voter_id = session['user_id']
    referendum_id = request.form['referendum_id']
    option_id = request.form['option_id']

    db = get_db()
    cursor = db.cursor()

    try:
        # 1️⃣ Insert vote
        cursor.execute(
            "INSERT INTO votes (voter_id, referendum_id, option_id) VALUES (%s,%s,%s)",
            (voter_id, referendum_id, option_id)
        )
        db.commit()
    except:
        return "You have already voted in this referendum."

    # 2️⃣ Count TOTAL registered voters
    cursor.execute("SELECT COUNT(*) FROM voters")
    total_voters = cursor.fetchone()[0]

    # 3️⃣ Count votes PER OPTION (this is the key)
    cursor.execute("""
        SELECT option_id, COUNT(*) AS vote_count
        FROM votes
        WHERE referendum_id=%s
        GROUP BY option_id
    """, (referendum_id,))

    results = cursor.fetchall()

    # 4️⃣ Close ONLY if one option reaches 50% of ALL voters
    for opt_id, vote_count in results:
        if vote_count > total_voters * 0.5:
            cursor.execute(
                "UPDATE referendums SET status='closed' WHERE referendum_id=%s",
                (referendum_id,)
            )
            db.commit()
            break
    print("DEBUG voter_id:", voter_id)

    return redirect('/voter/dashboard')

