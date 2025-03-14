from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector

# Define the blueprint
feedback_bp = Blueprint('feedback', __name__)

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dd"
)
cursor = conn.cursor()

@feedback_bp.route('/')
def home():
    # Redirect root URL to the feedback form
    return redirect(url_for('feedback.feedback_form'))

@feedback_bp.route('/feedback')
def feedback_form():
    return render_template('feedback.html')

@feedback_bp.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    # Fetch form data
    rating = request.form.get('rating')
    name = request.form.get('name')
    email = request.form.get('email')
    age = request.form.get('age')
    phone = request.form.get('phone')
    message = request.form.get('message')

    # Insert feedback into the database
    cursor.execute('''INSERT INTO feedback (rating, name, email, age, phone, message)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (rating, name, email, age, phone, message))
    conn.commit()

    # Redirect to thank-you page after submission
    return redirect(url_for('feedback.thank_you'))

@feedback_bp.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

