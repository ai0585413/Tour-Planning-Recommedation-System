from flask import Blueprint, render_template, request, jsonify
import mysql.connector

user_app = Blueprint('user_app', __name__)

# Centralize database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dd"
    )

# Route to display users
@user_app.route('/')
def show_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor here directly
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('user.html', data=users)

# Route to edit a user
@user_app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor here directly

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    address = request.form['address']
    phone = request.form['phone']

    cursor.execute("""
        UPDATE users
        SET first_name = %s, last_name = %s, username = %s, email = %s, address = %s, phone = %s
        WHERE user_id = %s
    """, (first_name, last_name, username, email, address, phone, user_id))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({'success': True})

# Route to delete a user
@user_app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor here directly
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({'success': True})

