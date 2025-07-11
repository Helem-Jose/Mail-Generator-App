from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    if (os.path.exists('instance/users.db')) == False:
        with app.app_context():
            db.create_all()