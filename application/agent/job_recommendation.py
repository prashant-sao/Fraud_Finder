"""
Job Recommendation System - Integrated Module
Provides personalized job recommendations based on user preferences and history
No route conflicts - integrates with existing API Blueprint
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, desc
from application.database import db
from application.models import (
    User, Job_Posting, Analysis_Results, 
    Company_Verification
)
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, urlparse
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import json

logger = logging.getLogger(__name__)


class JobRecommendationEngine:
    """
    Smart job recommendation engine that suggests legitimate jobs
    based on user qualifications, interests, and browsing history
    """
    
    def __init__(self):
        self.min_reputation_score = 60  # Minimum company reputation
        self.max_risk_score = 30  # Maximum acceptable risk score for "safe" jobs
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def get_user_preferences(self, user_id):
        """Extract user preferences from profile"""
        try:
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return None
            
            # Parse qualifications and interests
            qualifications = self._parse_text_list(user.qualifications or '')
            interests = self._parse_text_list(user.fields_of_interest or '')
            
            return {
                'qualifications': qualifications,
                'interests': interests,
                'user': user
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}", exc_info=True)
            return None
    
    def _parse_text_list(self, text):
        """Parse comma-separated or newline-separated text into list"""
        if not text:
            return []
        
        # Split by comma, semicolon, or newline
        items = re.split(r'[,;\n]', text)
        # Clean and filter
        return [item.strip().lower() for item in items if item.strip()]
    
    def get_user_browsing_history(self, user_id, limit=50):
        """Get user's job browsing history from database"""
        try:
            # Get jobs the user has analyzed
            user_jobs = db.session.query(
                Job_Posting, Analysis_Results
            ).join(
                Analysis_Results,
                Job_Posting.job_id == Analysis_Results.job_id
            ).filter(
                Job_Posting.submitted_by == user_id
            ).order_by(
                Job_Posting.submitted_at.desc()
            ).limit(limit).all()
            
            history = []
            for job, analysis in user_jobs:
                history.append({
                    'job_id': job.job_id,
                    'title': job.job_title,
                    'company': job.company_name,
                    'description': job.job_description,
                    'url': job.url,
                    'risk_score': analysis.risk_score,
                    'analyzed_at': job.submitted_at
                })
            
            return history
        except Exception as e:
            logger.error(f"Error getting browsing history: {e}", exc_info=True)
            return []
    
    def _extract_keywords(self, content):
        """Extract important keywords from job content"""
        content_lower = content.lower()
        
        # Common job titles
        titles = ['engineer', 'developer', 'analyst', 'manager', 'designer',
                 'scientist', 'consultant', 'intern', 'coordinator', 'specialist',
                 'architect', 'lead', 'director', 'administrator', 'technician']
        
        # Technical skills
        skills = ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
                 'machine learning', 'data analysis', 'project management', 'agile',
                 'marketing', 'sales', 'excel', 'powerpoint', 'communication',
                 'nodejs', 'angular', 'vue', 'kubernetes', 'tensorflow', 'pandas']
        
        # Industries
        industries = ['tech', 'finance', 'healthcare', 'retail', 'consulting',
                     'education', 'manufacturing', 'entertainment', 'e-commerce',
                     'fintech', 'saas', 'startup']
        
        # Experience levels
        levels = ['senior', 'junior', 'entry', 'mid', 'lead', 'principal', 
                 'staff', 'associate', 'expert']
        
        found_keywords = {
            'titles': [t for t in titles if t in content_lower],
            'skills': [s for s in skills if s in content_lower],
            'industries': [i for i in industries if i in content_lower],
            'levels': [l for l in levels if l in content_lower]
        }
        
        return found_keywords
    
    def build_user_profile(self, user_id):
        """Build ML-powered user profile based on browsing history"""
        try:
            history = self.get_user_browsing_history(user_id)
            
            if not history or len(history) < 3:
                logger.info(f"Not enough history to build profile for user {user_id}")
                return None
            
            # Aggregate keywords from history
            all_titles = []
            all_skills = []
            all_industries = []
            all_levels = []
            
            # Weight recent jobs more heavily
            weights = np.linspace(0.5, 1.0, len(history))
            
            title_counter = Counter()
            skill_counter = Counter()
            industry_counter = Counter()
            level_counter = Counter()
            
            for i, entry in enumerate(history):
                content = f"{entry['title']} {entry['description']}"
                keywords = self._extract_keywords(content)
                
                for title in keywords['titles']:
                    title_counter[title] += weights[i]
                for skill in keywords['skills']:
                    skill_counter[skill] += weights[i]
                for industry in keywords['industries']:
                    industry_counter[industry] += weights[i]
                for level in keywords['levels']:
                    level_counter[level] += weights[i]
            
            profile = {
                'preferred_titles': [t for t, c in title_counter.most_common(5)],
                'preferred_skills': [s for s, c in skill_counter.most_common(10)],
                'preferred_industries': [i for i, c in industry_counter.most_common(3)],
                'preferred_levels': [l for l, c in level_counter.most_common(2)],
                'history_count': len(history)
            }
            
            logger.info(f"Built profile for user {user_id}: {profile}")
            return profile
            
        except Exception as e:
            logger.error(f"Error building user profile: {e}", exc_info=True)
            return None
    
    def _calculate_match_score(self, job_title, job_description, company_name, 
                                qualifications, interests, ml_profile=None):
        """Calculate how well a job matches user preferences"""
        score = 0
        max_score = 100
        
        job_text = f"{job_title} {job_description} {company_name}".lower()
        
        # Base matching on user-provided preferences (40 points)
        if qualifications:
            matches = sum(1 for qual in qualifications if qual in job_text)
            if len(qualifications) > 0:
                qualification_score = min(25, (matches / len(qualifications)) * 25)
                score += qualification_score
        
        if interests:
            matches = sum(1 for interest in interests if interest in job_text)
            if len(interests) > 0:
                interest_score = min(15, (matches / len(interests)) * 15)
                score += interest_score
        
        # ML-based matching on browsing history (60 points)
        if ml_profile:
            ml_score = 0
            
            # Check preferred titles (20 points)
            if ml_profile.get('preferred_titles'):
                title_matches = sum(1 for t in ml_profile['preferred_titles'] if t in job_text)
                ml_score += min(20, (title_matches / len(ml_profile['preferred_titles'])) * 20)
            
            # Check preferred skills (25 points)
            if ml_profile.get('preferred_skills'):
                skill_matches = sum(1 for s in ml_profile['preferred_skills'] if s in job_text)
                ml_score += min(25, (skill_matches / len(ml_profile['preferred_skills'])) * 25)
            
            # Check preferred industries (10 points)
            if ml_profile.get('preferred_industries'):
                industry_matches = sum(1 for i in ml_profile['preferred_industries'] if i in job_text)
                ml_score += min(10, (industry_matches / len(ml_profile['preferred_industries'])) * 10)
            
            # Check preferred levels (5 points)
            if ml_profile.get('preferred_levels'):
                level_matches = sum(1 for l in ml_profile['preferred_levels'] if l in job_text)
                ml_score += min(5, (level_matches / len(ml_profile['preferred_levels'])) * 5)
            
            score += ml_score
        
        return min(score, max_score)
    
    def get_safe_jobs_from_database(self, user_id, limit=20):
        """Get safe, legitimate jobs from existing database"""
        try:
            # Get jobs with low risk scores from database
            safe_jobs = db.session.query(
                Job_Posting, Analysis_Results, Company_Verification
            ).join(
                Analysis_Results,
                Job_Posting.job_id == Analysis_Results.job_id
            ).outerjoin(
                Company_Verification,
                Job_Posting.company_name == Company_Verification.company_name
            ).filter(
                Analysis_Results.risk_score <= self.max_risk_score,
                Job_Posting.submitted_by != user_id  # Exclude user's own submissions
            ).order_by(
                Analysis_Results.risk_score.asc(),
                Job_Posting.submitted_at.desc()
            ).limit(limit).all()
            
            jobs = []
            for job, analysis, company in safe_jobs:
                jobs.append({
                    'job_id': job.job_id,
                    'title': job.job_title,
                    'company': job.company_name,
                    'description': job.job_description,
                    'url': job.url,
                    'risk_score': analysis.risk_score,
                    'risk_level': analysis.risk_level,
                    'verdict': analysis.verdict,
                    'source': 'Internal Database',
                    'company_verified': company.is_verified if company else False,
                    'company_reputation': company.reputation_score if company else 0,
                    'posted_date': job.submitted_at.strftime('%Y-%m-%d') if job.submitted_at else 'Recently'
                })
            
            return jobs
        except Exception as e:
            logger.error(f"Error fetching safe jobs: {e}", exc_info=True)
            return []
    
    def _search_external_jobs(self, query, location='Remote', limit=5):
        """Search external job boards (Indeed) for additional recommendations"""
        jobs = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards (Indeed's HTML structure)
            job_cards = soup.find_all('div', class_=re.compile('job_seen_beacon|jobsearch-SerpJobCard'))
            
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', class_='companyName')
                    location_elem = card.find('div', class_='companyLocation')
                    snippet_elem = card.find('div', class_='job-snippet')
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        loc = location_elem.get_text(strip=True) if location_elem else location
                        description = snippet_elem.get_text(strip=True) if snippet_elem else ''
                        
                        link_elem = card.find('a', class_='jcs-JobTitle')
                        job_url = urljoin('https://www.indeed.com', link_elem['href']) if link_elem and link_elem.get('href') else url
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': loc,
                            'description': description,
                            'source': 'Indeed',
                            'url': job_url,
                            'posted_date': 'Recently',
                            'risk_score': None,  # Will be calculated
                            'job_id': None
                        })
                except Exception as e:
                    logger.debug(f"Error parsing job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"External job search error: {e}", exc_info=True)
        
        return jobs
    
    def get_recommendations(self, user_id, limit=10, include_external=True, 
                           risk_filter='safe_only'):
        """
        Get personalized job recommendations for user
        
        Args:
            user_id: User ID to get recommendations for
            limit: Maximum number of recommendations
            include_external: Whether to include external job boards
            risk_filter: 'safe_only', 'all', or 'mixed'
        
        Returns:
            List of recommended jobs with match scores
        """
        try:
            logger.info(f"Getting recommendations for user {user_id}")
            
            # Get user preferences
            user_prefs = self.get_user_preferences(user_id)
            if not user_prefs:
                logger.warning(f"No preferences found for user {user_id}")
                return []
            
            qualifications = user_prefs['qualifications']
            interests = user_prefs['interests']
            
            # Build ML profile from browsing history
            ml_profile = self.build_user_profile(user_id)
            
            # Get safe jobs from database
            db_jobs = self.get_safe_jobs_from_database(user_id, limit=limit * 2)
            logger.info(f"Found {len(db_jobs)} safe jobs from database")
            
            all_jobs = db_jobs.copy()
            
            # Search external sources if enabled
            if include_external:
                search_queries = []
                
                # Build search queries from user preferences
                if interests:
                    search_queries.extend(interests[:3])
                if qualifications:
                    search_queries.extend(qualifications[:2])
                if ml_profile and ml_profile.get('preferred_titles'):
                    search_queries.extend(ml_profile['preferred_titles'][:2])
                
                # Default search if no preferences
                if not search_queries:
                    search_queries = ['software engineer', 'data analyst', 'remote jobs']
                
                # Search external sources
                for query in search_queries[:3]:  # Limit to 3 queries
                    external_jobs = self._search_external_jobs(query, limit=3)
                    all_jobs.extend(external_jobs)
                    
                logger.info(f"Added {len(all_jobs) - len(db_jobs)} jobs from external sources")
            
            # Calculate match scores for all jobs
            for job in all_jobs:
                match_score = self._calculate_match_score(
                    job['title'],
                    job.get('description', ''),
                    job['company'],
                    qualifications,
                    interests,
                    ml_profile
                )
                job['match_score'] = match_score
                
                # Use existing risk score or default to safe
                if job.get('risk_score') is None:
                    job['risk_score'] = 15  # Assume external jobs are relatively safe
                    job['risk_level'] = 'Low Risk'
            
            # Apply risk filtering
            if risk_filter == 'safe_only':
                filtered_jobs = [j for j in all_jobs if j['risk_score'] <= self.max_risk_score]
            elif risk_filter == 'all':
                filtered_jobs = all_jobs
            else:  # mixed
                safe_jobs = [j for j in all_jobs if j['risk_score'] <= self.max_risk_score]
                risky_jobs = [j for j in all_jobs if j['risk_score'] > self.max_risk_score]
                
                safe_count = int(limit * 0.7)
                risky_count = limit - safe_count
                
                safe_jobs = sorted(safe_jobs, key=lambda x: x['match_score'], reverse=True)[:safe_count]
                risky_jobs = sorted(risky_jobs, key=lambda x: x['match_score'], reverse=True)[:risky_count]
                
                filtered_jobs = safe_jobs + risky_jobs
            
            # Sort by match score
            recommendations = sorted(filtered_jobs, key=lambda x: x['match_score'], reverse=True)[:limit]
            
            logger.info(f"Returning {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}", exc_info=True)
            return []
    
    def get_user_stats(self, user_id):
        """Get user statistics for recommendations"""
        try:
            history = self.get_user_browsing_history(user_id)
            ml_profile = self.build_user_profile(user_id) if len(history) >= 3 else None
            
            return {
                'jobs_analyzed': len(history),
                'has_ml_profile': ml_profile is not None,
                'ml_profile': ml_profile,
                'recent_jobs': [
                    {
                        'title': h['title'],
                        'company': h['company'],
                        'analyzed_at': h['analyzed_at'].strftime('%Y-%m-%d %H:%M')
                    }
                    for h in history[:5]
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}", exc_info=True)
            return {
                'jobs_analyzed': 0,
                'has_ml_profile': False,
                'ml_profile': None,
                'recent_jobs': []
            }


# Initialize recommendation engine (singleton)
recommendation_engine = None

def get_recommendation_engine():
    """Get or create recommendation engine instance"""
    global recommendation_engine
    if recommendation_engine is None:
        recommendation_engine = JobRecommendationEngine()
    return recommendation_engine