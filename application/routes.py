from flask import Blueprint, jsonify, request, render_template
from flask_security import auth_required, current_user, login_user
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

api_bp = Blueprint('api_bp', __name__)



# Initialize the corporate agent
fraud_detector = CorporateAgent()

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
            
            # Scrape content from URL
            scraped_content = scrape_job_posting(job_url)
            if not scraped_content:
                return jsonify({'error': 'Failed to scrape job posting from URL'}), 400
            
            job_text = scraped_content
            
        elif not job_text:
            return jsonify({'error': 'Either job_text or job_url must be provided'}), 400
        
        # Perform fraud analysis
        analysis_result = fraud_detector.analyze_job_post(job_text)
        
        # Determine if it's a scam based on risk score
        risk_score = analysis_result['risk_score']
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
        
        # Generate auto-reply
        auto_reply = generate_auto_reply(is_scam)
        
        # Prepare detailed response
        response_data = {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'is_scam': is_scam,
            'auto_reply': auto_reply,
            'analysis': {
                'red_flags': analysis_result['red_flags'],
                'company_legitimacy': analysis_result['company_legitimacy'],
                'scam_database_check': analysis_result['scam_result'],
                'llm_analysis': analysis_result['llm_analysis'] if analysis_type == 'detailed' else None,
                'company_info': {
                    'name': analysis_result.get('company_name'),
                    'website': analysis_result.get('company_website')
                }
            },
            'recommendations': generate_recommendations(analysis_result, risk_score),
            'analysis_type': analysis_type
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

def generate_recommendations(analysis_result, risk_score):
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    if risk_score >= 60:
        recommendations.append("Do not proceed with this job opportunity")
        recommendations.append("Report this posting to the job board")
        
    if analysis_result['red_flags']:
        recommendations.append("Multiple red flags detected - exercise extreme caution")
        
    if not analysis_result['company_legitimacy']['website_exists']:
        recommendations.append("Company website could not be verified")
        
    if not analysis_result['company_legitimacy']['linkedin_exists']:
        recommendations.append("Company LinkedIn page not found")
        
    if analysis_result['scam_result']['email_flagged'] or analysis_result['scam_result']['phone_flagged']:
        recommendations.append("Contact information flagged in scam database")
        
    if risk_score < 40:
        recommendations.append("Job posting appears legitimate, but always verify independently")
        recommendations.append("Research the company thoroughly before applying")
        
    return recommendations

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