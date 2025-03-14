from flask import Blueprint, render_template, request, jsonify
import mysql.connector

select_app = Blueprint('select_app', __name__)

# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dd"
)
cursor = db.cursor(dictionary=True)

@select_app.route('/')
def display_user_routes():
    query = """
    SELECT users.user_id,  users.username, users.email,
           user_selected_routes.id as route_id,
           user_selected_routes.selected_route
    FROM users
    NATURAL JOIN user_selected_routes
    """
    cursor.execute(query)
    joined_data = cursor.fetchall()
    return render_template('user_routes.html', data=joined_data)
@select_app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user_details(user_id):
    if request.method == 'POST':
        # Update user information
        try:


            username = request.form['username']
            email = request.form['email']



            update_query = """
            UPDATE users
            SET  username = %s, email = %s
            WHERE user_id = %s
            """
            cursor.execute(update_query, (username, email, user_id))
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

@select_app.route('/delete_route/<int:route_id>', methods=['POST'])
def delete_user_selected_route(route_id):
    delete_query = "DELETE FROM user_selected_routes WHERE id = %s"
    cursor.execute(delete_query, (route_id,))
    db.commit()
    return jsonify(success=True)

