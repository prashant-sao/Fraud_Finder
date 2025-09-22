from flask import current_app as app,jsonify,request,render_template,send_from_directory
from flask_security import auth_required,current_user,login_user
from werkzeug.security import generate_password_hash, check_password_hash
from application.database import db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    credentials = request.get_json()

    if app.security.datastore.find_user(email=credentials['email']):
        return jsonify({"message": "User already exists"}), 400
    new_user = app.security.datastore.create_user(
        email=credentials['email'],
        username=credentials['username'], 
        password=generate_password_hash(credentials['password']),
        qualifications=credentials['qualification'],
        fields_of_interest=credentials['fields_of_interest']
    )

    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    user = app.security.datastore.find_user(username=username)
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'message': 'Login successful!'}), 200
    else:
        return jsonify({'message': 'Invalid username or password!'}), 401
    
@app.route('/edit_profile', methods=['PUT'])
@auth_required('token')
def edit_profile():
    data = request.get_json()
    user = app.security.datastore.find_user(id=current_user.id)

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    if 'qualifications' in data:
        user.qualifications = data['qualifications']
    if 'fields_of_interest' in data:
        user.fields_of_interest = data['fields_of_interest']

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully!'}), 200

@app.route('/api/history', methods=['GET'])
@auth_required('token')
def get_history():
    user = app.security.datastore.find_user(id=current_user.id)
    reports = user.fraud_reports
    history = [
        {
            'id': report.id,
            'title': report.title,
            'description': report.description,
            'fraud_score': report.fraud_score
        } for report in reports
    ]
    return jsonify(history), 200
  