from flask import Blueprint, render_template, request, jsonify
import mysql.connector

review_app = Blueprint('review_app', __name__)

# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dd"
)
cursor = db.cursor(dictionary=True)

@review_app.route('/')
def display_feedback():
    # Fetch all records from feedback table
    cursor.execute("SELECT * FROM feedback")
    feedback_data = cursor.fetchall()
    return render_template('review.html', data=feedback_data)

@review_app.route('/edit_feedback/<int:feedback_id>', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    if request.method == 'POST':
        # Update feedback information
        try:
            rating = request.form['rating']
            name = request.form['name']
            email = request.form['email']
            age = request.form['age']
            phone = request.form['phone']
            message = request.form['message']

            update_query = """
            UPDATE feedback
            SET rating = %s, name = %s, email = %s, age = %s, phone = %s, message = %s
            WHERE id = %s
            """
            cursor.execute(update_query, (rating, name, email, age, phone, message, feedback_id))
            db.commit()
            return jsonify(success=True)
        except Exception as e:
            print(f"Error updating feedback: {e}")
            return jsonify(success=False)
    else:
        # Fetch current feedback data for editing
        cursor.execute("SELECT * FROM feedback WHERE id = %s", (feedback_id,))
        feedback_data = cursor.fetchone()
        return jsonify(feedback_data)

@review_app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    delete_query = "DELETE FROM feedback WHERE id = %s"
    cursor.execute(delete_query, (feedback_id,))
    db.commit()
    return jsonify(success=True)


