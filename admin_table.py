from flask import Blueprint, render_template, request, jsonify
import mysql.connector

admin_app = Blueprint('admin_app', __name__)

# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dd"
)
cursor = db.cursor(dictionary=True)

@admin_app.route('/')
def display_joined_data():
    query = """
    SELECT users.user_id,  users.username, routes.id as route_id, routes.start_location,
           routes.end_location, routes.duration, routes.route
    FROM users
    NATURAL JOIN routes
    """
    cursor.execute(query)
    joined_data = cursor.fetchall()
    return render_template('di.html', data=joined_data)

@admin_app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        # Update user information
        try:
            username = request.form['username']

            update_query = """
            UPDATE users
            SET username = %s
            WHERE user_id = %s
            """
            cursor.execute(update_query, (username, user_id))
            db.commit()
            return jsonify(success=True)
        except Exception as e:
            print(f"Error updating user information: {e}")
            return jsonify(success=False)
    else:
        # Fetch current user data
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        return jsonify(user_data)

@admin_app.route('/delete/<int:route_id>', methods=['POST'])
def delete_route(route_id):
    delete_query = "DELETE FROM routes WHERE id = %s"
    cursor.execute(delete_query, (route_id,))
    db.commit()
    return jsonify(success=True)


