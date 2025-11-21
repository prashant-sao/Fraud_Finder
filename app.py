"""from flask import Flask
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from werkzeug.security import generate_password_hash, check_password_hash
from application.config import LocalDevlopmentConfig
from application.database import db
from application.models import User, Role


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fraud_detection.db'
    app.config.from_object(LocalDevlopmentConfig)
    
    # Enable CORS
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    
    # Add after_request handler INSIDE create_app, not in with block
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Import and register blueprints INSIDE create_app
    from application.routes import api_bp
    api_bp.security = app.security
    app.register_blueprint(api_bp)
    
    return app    


app = create_app()    


with app.app_context():
    db.create_all()  # Create database tables if they don't exist
    
    app.security.datastore.find_or_create_role(name='admin')
    app.security.datastore.find_or_create_role(name='user')
    db.session.commit() 

    if not app.security.datastore.find_user(email='admin@123.com'):
        admin_user = app.security.datastore.create_user(
            email='admin@123.com', 
            username='admin', 
            password=generate_password_hash('admin123'), 
            roles=['admin', 'user']
        )
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.security import generate_password_hash
from application.config import LocalDevlopmentConfig
from application.database import db
from application.models import User, Role


FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_FOLDER,
        template_folder=FRONTEND_FOLDER
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fraud_detection.db'
    app.config.from_object(LocalDevlopmentConfig)

    # Enable CORS for API only
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)

    db.init_app(app)

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)

    # Global CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # REST API
    from application.routes import api_bp
    api_bp.security = app.security
    app.register_blueprint(api_bp)

    # ---------- Serve React Frontend -----------
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_FOLDER, "index.html")

    # Catch-all route for React Router
    @app.route("/<path:path>")
    def static_proxy(path):
        file_path = os.path.join(FRONTEND_FOLDER, path)

        if os.path.isfile(file_path):
            return send_from_directory(FRONTEND_FOLDER, path)

        return send_from_directory(FRONTEND_FOLDER, "index.html")
    # -------------------------------------------

    return app


app = create_app()

with app.app_context():
    db.create_all()

    app.security.datastore.find_or_create_role(name='admin')
    app.security.datastore.find_or_create_role(name='user')
    db.session.commit()

    if not app.security.datastore.find_user(email='admin@123.com'):
        admin_user = app.security.datastore.create_user(
            email='admin@123.com',
            username='admin',
            password=generate_password_hash('admin123'),
            roles=['admin', 'user']
        )
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
