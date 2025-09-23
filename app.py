from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore,hash_password
from werkzeug.security import generate_password_hash, check_password_hash
from application.config import LocalDevlopmentConfig
from application.database import db
from application.models import User, Role


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fraud_detection.db'
    app.config.from_object(LocalDevlopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    app.app_context().push()
    return app    

app = create_app()    


with app.app_context():
    db.create_all()  # Create database tables if they don't exist
    
    app.security.datastore.find_or_create_role(name='admin')
    app.security.datastore.find_or_create_role(name='user')
    db.session.commit() 

    if not app.security.datastore.find_user(email='admin@123.com'):
        admin_user = app.security.datastore.create_user(email ='admin@123.com', 
                                                        username='admin', 
                                                        password=generate_password_hash('admin123'), 
                                                        roles=['admin','user'])
    
        db.session.add(admin_user)  # Add the admin user to the session
        app.security.datastore.add_role_to_user(admin_user, 'admin')  # Assign the admin role
    db.session.commit()

    from application.routes import *

    if __name__ == '__main__':
        app.run(debug=True)