from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Session configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

    db.init_app(app)

    from .routes.auth import auth
    from .routes.item import item

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(item, url_prefix='/items')

    @app.route("/")
    def root():
        return render_template("items/landing.html")


    migrate = Migrate(app, db)

    return app