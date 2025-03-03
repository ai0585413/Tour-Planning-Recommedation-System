from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import os
import re
import logging
from flask_cors import CORS
from dotenv import load_dotenv
from merge import merge_app
from feedback import feedback_bp
from rou import routes_app
from map import map_app

app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()

# Enable CORS for cross-domain requests
CORS(app)
app.register_blueprint(merge_app, url_prefix='/merge')
app.register_blueprint(routes_app, url_prefix='/routes')
app.register_blueprint(feedback_bp, url_prefix='/feedback')
app.register_blueprint(map_app, url_prefix='/map')
# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Set up MySQL connection
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dd',
}
conn = mysql.connector.connect(**db_config)

# Secret key for session management
app.secret_key = os.getenv('SECRET_KEY', 'your_strong_secret_key')

# Create database tables if they don't exist
def create_user_table():
    with conn.cursor() as cursor:
        query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL
        )
        """
        cursor.execute(query)
    conn.commit()

create_user_table()

# User registration
def register_user(username, email):
    with conn.cursor() as cursor:
        query = """
        INSERT INTO users (username, email)
        VALUES (%s, %s)
        """
        cursor.execute(query, (username, email))
    conn.commit()

# Check if username or email exists
def check_existing_user(username, email):
    with conn.cursor() as cursor:
        query = "SELECT username, email FROM users WHERE username = %s OR email = %s"
        cursor.execute(query, (username, email))
        return cursor.fetchone()

# Retrieve user by username
def get_user_by_username(username):
    with conn.cursor() as cursor:
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchone()
@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact us.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        # Retrieve the user based on username
        user = get_user_by_username(username)

        if user:
            # Check if the email matches
            if user[2] == email:  # Assuming email is the 3rd column in the `users` table
                # Set session and redirect to home
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                return redirect(url_for('merge_app.index'))
            else:
                flash('Incorrect email for this username.', 'error')
                return redirect(url_for('login'))
        else:
            logging.warning("Username not found.")
            flash('Username not found', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Basic form validation
        if not all([username, email]):
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Invalid email format!', 'error')
            return redirect(url_for('register'))

        # Check if username or email already exists
        if check_existing_user(username, email):
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))

        try:
            register_user(username, email)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error during registration: {e}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')





if __name__ == '__main__':
    app.run(debug=True)
