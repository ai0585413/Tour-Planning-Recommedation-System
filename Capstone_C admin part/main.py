from flask import Flask, render_template
from admin_table import admin_app
from review import review_app
from admin_user import select_app

app = Flask(__name__)
app.register_blueprint(review_app, url_prefix='/review')
app.register_blueprint(admin_app, url_prefix='/admin')
app.register_blueprint(select_app, url_prefix='/select')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)

