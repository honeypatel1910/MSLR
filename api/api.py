from flask import Blueprint, jsonify, request
from db.db import get_db

api = Blueprint('api', __name__)

@api.route('/mslr/referendums')
def get_referendums_by_status():
    status = request.args.get('status')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM referendums WHERE status=%s",
        (status,)
    )
    referendums = cursor.fetchall()

    result = []

    for ref in referendums:
        cursor.execute("""
            SELECT o.option_id, o.option_text, COUNT(v.vote_id) AS votes
            FROM referendum_options o
            LEFT JOIN votes v ON o.option_id = v.option_id
            WHERE o.referendum_id = %s
            GROUP BY o.option_id
        """, (ref['referendum_id'],))

        options = []
        for opt in cursor.fetchall():
            options.append({
                str(opt['option_id']): opt['option_text'],
                "votes": str(opt['votes'])
            })

        result.append({
            "referendum_id": str(ref['referendum_id']),
            "status": ref['status'],
            "referendum_title": ref['title'],
            "referendum_desc": ref['description'],
            "referendum_options": {
                "options": options
            }
        })

    return jsonify({"Referendums": result})

@api.route('/mslr/referendum/<int:ref_id>')
def get_referendum_by_id(ref_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM referendums WHERE referendum_id=%s",
        (ref_id,)
    )
    ref = cursor.fetchone()

    if not ref:
        return jsonify({}), 404

    cursor.execute("""
        SELECT o.option_id, o.option_text, COUNT(v.vote_id) AS votes
        FROM referendum_options o
        LEFT JOIN votes v ON o.option_id = v.option_id
        WHERE o.referendum_id = %s
        GROUP BY o.option_id
    """, (ref_id,))

    options = []
    for opt in cursor.fetchall():
        options.append({
            str(opt['option_id']): opt['option_text'],
            "votes": str(opt['votes'])
        })

    return jsonify({
        "referendum_id": str(ref['referendum_id']),
        "status": ref['status'],
        "referendum_title": ref['title'],
        "referendum_desc": ref['description'],
        "referendum_options": {
            "options": options
        }
    })
