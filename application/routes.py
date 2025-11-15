from flask import Blueprint, jsonify, request, render_template
from flask_security import auth_required, current_user, login_user,logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from application.database import db
import requests
from bs4 import BeautifulSoup
import re
import logging

# Import your fraud detection modules
from application.agent.corporate_agent import CorporateAgent
from application.agent.auto_reply import generate_auto_reply
from application.agent.scam_checker import add_scam_to_database

from application.agent.risk_score import JobFraudDetector
from application.agent.job_recommendation import ml_recommender


fraud_detector = JobFraudDetector()

api_bp = Blueprint('api_bp', __name__)



# Initialize the corporate agent
Corporate_agent = CorporateAgent()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_bp.route('/')
def index():
    return render_template('frontend/index.html')

@api_bp.route('/api/register', methods=['POST'])
def register():
    try:
        credentials = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if not credentials.get(field):
                return jsonify({"message": f"{field} is required"}), 400
        
        # Check if user already exists
        if api_bp.security.datastore.find_user(email=credentials['email']):
            return jsonify({"message": "User already exists"}), 400
            
        if api_bp.security.datastore.find_user(username=credentials['username']):
            return jsonify({"message": "Username already taken"}), 400
        
        new_user = api_bp.security.datastore.create_user(
            email=credentials['email'],
            username=credentials['username'], 
            password=generate_password_hash(credentials['password']),
            qualifications=credentials.get('qualification', ''),
            fields_of_interest=credentials.get('fields_of_interest', '')
        )
        
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Registration failed"}), 500

@api_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')  # Changed from username to email
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required!'}), 400

        # Find user by email
        user = api_bp.security.datastore.find_user(email=email)
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid email or password!'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@api_bp.route('/api/logout', methods=['POST'])
def logout_simple():
    """Simple logout endpoint that doesn't require authentication"""
    try:
        # This version works even if the token has expired or is invalid
        logout_user()
        
        return jsonify({
            'message': 'Logout successful!',
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Simple logout error: {str(e)}")
        return jsonify({
            'message': 'Logout successful ',
            'success': True
        }), 200  

@api_bp.route('/api/edit_profile', methods=['PUT'])
@auth_required('token')
def edit_profile():
    try:
        data = request.get_json()
        user = api_bp.security.datastore.find_user(id=current_user.id)

        if 'username' in data:
            # Check if username is already taken by another user
            existing_user = api_bp.security.datastore.find_user(username=data['username'])
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'message': 'Username already taken!'}), 400
            user.username = data['username']
            
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = api_bp.security.datastore.find_user(email=data['email'])
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'message': 'Email already taken!'}), 400
            user.email = data['email']
            
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        if 'qualifications' in data:
            user.qualifications = data['qualifications']
        if 'fields_of_interest' in data:
            user.fields_of_interest = data['fields_of_interest']

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Profile update failed'}), 500

def scrape_job_posting(url):
    """Scrape job posting content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit text length
        
    except requests.RequestException as e:
        logger.error(f"Scraping error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected scraping error: {str(e)}")
        return None

@api_bp.route('/api/analyze', methods=['POST'])
def analyze_job_posting():
    """Main API endpoint for analyzing job postings"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        job_text = data.get('job_text', '').strip()
        job_url = data.get('job_url', '').strip()
        analysis_type = data.get('analysis_type', 'quick')  # 'quick' or 'detailed'
        user_id = data.get('user_id')  # Get user_id if provided
        
        # Determine input source
        if job_url:
            # Validate URL format
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(job_url):
                return jsonify({'error': 'Invalid URL format'}), 400
            
            # Use the fraud_detector to fetch content from URL
            fetch_result = fraud_detector.fetch_job_posting(job_url)
            
            if not fetch_result['success']:
                return jsonify({'error': f'Failed to fetch job posting: {fetch_result["error"]}'}), 400
            
            job_text = fetch_result['content']
            
        elif not job_text:
            return jsonify({'error': 'Either job_text or job_url must be provided'}), 400
        
        # Set URL if not provided
        if not job_url:
            job_url = 'https://example.com/manual-entry'
        
        # Perform fraud analysis using the JobFraudDetector class
        # This will automatically save to database
        analysis_result = fraud_detector.analyze_job_posting(
            content=job_text,
            url=job_url,
            user_id=user_id,
            save_to_db=True
        )
        
        # Extract data from analysis_result
        risk_score = analysis_result['fraud_score']
        is_scam = risk_score >= 60  # Threshold for scam classification
        
        # Generate risk level
        if risk_score >= 80:
            risk_level = 'High'
            risk_color = 'danger'
        elif risk_score >= 40:
            risk_level = 'Medium'
            risk_color = 'warning'
        else:
            risk_level = 'Low'
            risk_color = 'success'
        
        # Generate auto-reply (you'll need to implement this function)
        auto_reply = generate_auto_reply(is_scam)
        
        # Prepare response matching your original format
        response_data = {
            'success': True,
            'url': job_url,
            'job_id': analysis_result.get('job_id'),
            'analysis_id': analysis_result.get('analysis_id'),
            'job_title': analysis_result['job_title'],
            'fraud_score': risk_score,
            'verdict': analysis_result['verdict'],
            'risk_level': analysis_result['risk_level'],
            'risk_color': risk_color,
            'is_scam': is_scam,
            'auto_reply': auto_reply,
            'red_flags': analysis_result['red_flags'],
            'details': analysis_result['details'],
            'analysis': {
                'red_flags': analysis_result['red_flags'],
                'company_legitimacy': {
                    'has_website': not analysis_result['red_flags'].get('no_company_website', True),
                    'has_linkedin': not analysis_result['red_flags'].get('no_linkedin', True),
                    'company_info_present': not analysis_result['red_flags'].get('no_company_info', True)
                },
                'company_info': {
                    'name': analysis_result.get('company_name'),
                    'website': analysis_result['details'].get('company_website')
                }
            },
            'recommendations': generate_recommendations(analysis_result, risk_score),
            'analysis_type': analysis_type
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


# Helper function for generating auto-reply (implement as needed)
def generate_auto_reply(is_scam):
    """Generate automated reply based on scam detection"""
    if is_scam:
        return {
            'message': 'Warning: This job posting shows multiple fraud indicators. Exercise extreme caution.',
            'action': 'Do not proceed without thorough verification.'
        }
    else:
        return {
            'message': 'This job posting appears legitimate based on our analysis.',
            'action': 'Still verify company details independently before proceeding.'
        }


# Helper function for generating recommendations
def generate_recommendations(analysis_result, risk_score):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if analysis_result['red_flags'].get('no_company_website'):
        recommendations.append('Verify the company has a legitimate website')
    
    if analysis_result['red_flags'].get('no_linkedin'):
        recommendations.append('Check if the company has a LinkedIn presence')
    
    if analysis_result['red_flags'].get('suspicious_contact'):
        recommendations.append('Be cautious of personal email addresses for business communication')
    
    if analysis_result['red_flags'].get('unrealistic_salary'):
        recommendations.append('Verify salary claims are realistic for the position and industry')
    
    if analysis_result['red_flags'].get('requests_personal_details'):
        recommendations.append('NEVER provide sensitive personal information before proper verification')
    
    if risk_score >= 70:
        recommendations.append('Consider reporting this job posting to the platform')
        recommendations.append('Do not proceed with application')
    
    return recommendations

@api_bp.route('/api/ml_recommend', methods=['POST'])
def ml_recommend():
    """
    ML-powered personalized job recommendations
    
    Request body:
    {
        "user_id": 123,
        "limit": 10,  // optional, default 10
        "risk_filter": "mixed"  // optional: "mixed", "safe_only", "risky_only", "all"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get optional parameters
        limit = data.get('limit', 10)
        risk_filter = data.get('risk_filter', 'mixed')
        
        # Validate limit
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            return jsonify({'error': 'limit must be between 1 and 50'}), 400
        
        # Validate risk_filter
        valid_filters = ['mixed', 'safe_only', 'risky_only', 'all']
        if risk_filter not in valid_filters:
            return jsonify({'error': f'risk_filter must be one of: {", ".join(valid_filters)}'}), 400
        
        logger.info(f"Getting ML recommendations for user {user_id}, limit={limit}, filter={risk_filter}")
        
        # Get personalized recommendations
        recommendations = ml_recommender.get_personalized_recommendations(
            user_id=user_id,
            limit=limit,
            risk_filter=risk_filter
        )
        
        # Get user stats
        user_stats = ml_recommender.get_user_stats(user_id)
        
        response_data = {
            'success': True,
            'user_id': user_id,
            'total_recommendations': len(recommendations),
            'risk_filter': risk_filter,
            'user_stats': user_stats,
            'recommendations': recommendations
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"ML recommendation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'ML recommendation failed: {str(e)}'
        }), 500


@api_bp.route('/api/ml_recommend/profile', methods=['GET'])
def get_ml_profile():
    """
    Get user's ML profile and preferences
    
    Query params:
    - user_id: required
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        user_stats = ml_recommender.get_user_stats(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'stats': user_stats
        }), 200
        
    except Exception as e:
        logger.error(f"ML profile error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get ML profile: {str(e)}'
        }), 500


@api_bp.route('/api/ml_recommend/history', methods=['GET'])
def get_ml_history():
    """
    Get user's job browsing history
    
    Query params:
    - user_id: required
    - limit: optional (default 20)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        history = ml_recommender.get_user_history(user_id)
        
        # Limit results
        history = history[:limit]
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'total_history': len(history),
            'history': history
        }), 200
        
    except Exception as e:
        logger.error(f"ML history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get ML history: {str(e)}'
        }), 500

@api_bp.route('/api/report_scam', methods=['POST'])
def report_scam():
    """API endpoint for reporting scam job postings"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        phone = data.get('phone')
        additional_info = data.get('additional_info', '')
        
        if not email and not phone:
            return jsonify({'error': 'Either email or phone must be provided'}), 400
        
        # Add to scam database
        add_scam_to_database(email or '', phone or '')
        
        # Log the report
        logger.info(f"Scam reported - Email: {email}, Phone: {phone}, Info: {additional_info}")
        
        return jsonify({'message': 'Thank you for reporting. The information has been added to our scam database.'}), 200
        
    except Exception as e:
        logger.error(f"Report scam error: {str(e)}")
        return jsonify({'error': 'Failed to report scam'}), 500

@api_bp.route('/api/recent_alerts', methods=['GET'])
def get_recent_alerts():
    """API endpoint for getting recent fraud alerts"""
    try:
        # This would typically come from your database
        # For now, returning mock data similar to your landing page
        recent_alerts = [
            {
                'id': 1,
                'title': 'Phishing Scam Alert',
                'description': 'Impersonating a well-known bank',
                'risk_level': 'High Risk',
                'category': 'Email',
                'time_ago': '2h ago'
            },
            {
                'id': 2,
                'title': 'Investment Fraud Scheme',
                'description': 'Promising high returns on crypto',
                'risk_level': 'Medium Risk',
                'category': 'Social Media',
                'time_ago': '4h ago'
            },
            {
                'id': 3,
                'title': 'Fake Online Store',
                'description': 'Offering discounted electronics',
                'risk_level': 'Low Risk',
                'category': 'Website',
                'time_ago': '6h ago'
            }
        ]
        
        return jsonify(recent_alerts), 200
        
    except Exception as e:
        logger.error(f"Recent alerts error: {str(e)}")
        return jsonify({'error': 'Failed to fetch recent alerts'}), 500

@api_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint for getting fraud detection statistics"""
    try:
        # This would typically come from your database
        stats = {
            'total_analyzed': 15420,
            'scams_detected': 3890,
            'accuracy_rate': 94.2,
            'users_protected': 12530
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500