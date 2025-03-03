import logging
from flask import flash
from flask import Blueprint, render_template, session, redirect, url_for, request
import mysql.connector

# Define the blueprint
routes_app = Blueprint('routes_app', __name__)

# Database connection configuration (adjust with your own credentials)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dd'
}


@routes_app.route('/recent_routes', methods=['GET', 'POST'])
def recent_routes():
    user_id = session.get('user_id')
    if not user_id:
        # If the user is not logged in, flash a message and redirect to the login page
        flash('Please register or log in to view recent routes.', 'error')
        return redirect(url_for('login'))

    # If user is logged in, continue with the rest of the logic
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        route_id = request.form.get('route_id')
        if route_id:
            try:
                # Handle route selection
                query = "SELECT route FROM routes WHERE id = %s AND user_id = %s"
                cursor.execute(query, (route_id, user_id))
                selected_route = cursor.fetchone()

                if selected_route:
                    # Insert the new selection into the user_selected_routes table
                    insert_query = "INSERT INTO user_selected_routes (user_id, selected_route) VALUES (%s, %s)"
                    cursor.execute(insert_query, (user_id, selected_route['route']))
                    db.commit()

                    flash('Route selected successfully!', 'success')
                    return redirect(url_for('routes_app.final_selection'))
            except mysql.connector.Error as e:
                logging.error(f"Error during route selection: {e}")
                flash('An error occurred while selecting the route.', 'error')

    # Query to get the 5 most recent routes for the logged-in user
    query = """
        SELECT id, route
        FROM routes
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 3
    """
    cursor.execute(query, (user_id,))
    routes = cursor.fetchall()

    # Render the routes in a template for the user to select
    return render_template('recent_routes.html', routes=routes)


@routes_app.route('/final_selection')
def final_selection():
    user_id = session.get('user_id')  # Get the logged-in user ID from the session

    if user_id:
        # Connect to the database

        # Render the final_selection.html with the selected route
        return render_template('final_selection.html')

@routes_app.route('/logout')
def logout():
    session.clear()  # Clears all session data, effectively logging out the user
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))


