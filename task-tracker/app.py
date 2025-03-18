from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config
import os
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

# Initialize Flask
app = Flask(__name__, template_folder="templates")  #Tells Flask where HTML templates are
app.config.from_object(config)

# Initialize Database (Don't Create Another SQLAlchemy Instance!)
from models import db  #Use the existing `db` from models.py
db.init_app(app)  #Correctly attach the database to the app

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect users to login page if not logged in

# User loader function (REQUIRED for Flask-Login)
from models import User  #Only import once!
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes AFTER setting up everything
from routes import *

# Run Flask
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  #Ensure the database is created
    app.run(debug=True)
