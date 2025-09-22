from application.database import db
from flask_security import UserMixin,RoleMixin

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    qualifications = db.Column(db.String(120), nullable=True)
    fields_of_interest = db.Column(db.String(250), nullable=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'Role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id'))

class Job_Posting(db.Model):
    __tablename__ = 'Job_Posting'
    job_id = db.Column(db.Integer,primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    extracted_entities = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

class Trending_Fraud_Job(db.Model):
    __tablename__ = 'Trending_Fraud_Job'
    trend_id = db.Column(db.Integer, primary_key=True)
    last_udated = db.Column(db.DateTime, nullable=False)
    popularity_score = db.Column(db.Float, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('Job_Posting.job_id'), nullable=False)
    fields_of_interest = db.Column(db.String(250),db.ForeignKey('User'), nullable=True)

class analysis_results(db.model):
    __tablename__ = 'analysis_results'
    analysis_id = db.Column(db.Integer, primary_key=True)
    risk_score = db.Column(db.Float, nullable=False)
    summary_labels = db.Column(db.Text, nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('Job_Posting.job_id'), nullable=False)

class company_verification(db.Model):
    __tablename__ = 'company_verification'
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    linkedin_url = db.Column(db.String(200), nullable=True)
    website_url = db.Column(db.String(200), nullable=True)
    social_presence = db.Column(db.Boolean, nullable=False)
    reputation_score = db.Column(db.Float, nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False)

class community_reports(db.Model):
    __tablename__ = 'community_reports'
    report_id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.DateTime, nullable=False)
    report_reason = db.Column(db.Text, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('Job_Posting.job_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)


class fraud_indicators(db.Model):
    __tablename__ = 'fraud_indicators'
    indicator_id = db.Column(db.Integer, primary_key=True)
    indicator_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity_level = db.Column(db.String(50), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_results.analysis_id'), nullable=False)

   

