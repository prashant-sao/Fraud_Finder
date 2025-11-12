from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, urljoin, urlparse
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import json
from datetime import datetime
import time
import sqlite3
from contextlib import contextmanager


# Import fraud detection logic
class JobFraudDetector:
    def _init_(self):
        self.salary_red_flags = [
            'guaranteed income', 'unlimited earning', 'earn thousands weekly',
            'work from home earn', 'no experience high pay', 'quick money'
        ]
        
        self.description_red_flags = [
            'act now', 'limited time', 'urgent', 'immediate start',
            'no experience necessary', 'easy money', 'risk free',
            'investment required', 'pay to apply', 'processing fee',
            'training fee', 'starter kit'
        ]

    def quick_analyze(self, job_title, job_company, job_description, job_url):
        """Quick fraud analysis for recommended jobs"""
        content = f"{job_title} {job_company} {job_description}".lower()
        fraud_score = 0
        red_flags = []
        risk_level = "Low Risk"

        # Check 1: Vague description (15 points)
        if len(job_description.split()) < 30:
            fraud_score += 15
            red_flags.append('vague_description')

        # Check 2: Unrealistic salary promises (20 points)
        for flag in self.salary_red_flags:
            if flag in content:
                fraud_score += 20
                red_flags.append('unrealistic_salary')
                break

        # Check 3: Suspicious keywords (20 points)
        suspicious_count = sum(1 for flag in self.description_red_flags if flag in content)
        if suspicious_count >= 2:
            fraud_score += 20
            red_flags.append('suspicious_keywords')

        # Check 4: Company verification (15 points)
        if not job_company or job_company == 'N/A' or len(job_company) < 3:
            fraud_score += 15
            red_flags.append('no_company_info')

        # Check 5: Personal email domains (15 points)
        if re.search(r'@(gmail|yahoo|hotmail|outlook)\.com', content):
            fraud_score += 15
            red_flags.append('personal_email')

        # Check 6: URL verification (15 points)
        domain = urlparse(job_url).netloc
        trusted_domains = ['indeed.com', 'linkedin.com', 'glassdoor.com', 'remoteok.com', 'weworkremotely.com']
        if not any(trusted in domain for trusted in trusted_domains):
            fraud_score += 10
            red_flags.append('unverified_source')

        # Determine risk level
        if fraud_score >= 60:
            risk_level = "High Risk"
            verdict = "Potentially Fraudulent"
        elif fraud_score >= 30:
            risk_level = "Medium Risk"
            verdict = "Proceed with Caution"
        else:
            risk_level = "Low Risk"
            verdict = "Appears Legitimate"

        return {
            'fraud_score': min(fraud_score, 100),
            'risk_level': risk_level,
            'verdict': verdict,
            'red_flags': red_flags,
            'is_safe': fraud_score < 30
        }

fraud_detector = JobFraudDetector()

class MLJobRecommender:
    def _init_(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def get_user_history(self, user_id):
        """Get user's job browsing history from database"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT job_url, job_content, job_title, job_company, analyzed_at
                FROM user_job_history
                WHERE user_id = ?
                ORDER BY analyzed_at DESC
                LIMIT 50
            ''', (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def add_to_history(self, user_id, url, content, title="", company=""):
        """Add analyzed job to user history in database"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Insert into history
            cursor.execute('''
                INSERT INTO user_job_history (user_id, job_url, job_content, job_title, job_company)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, url, content, title, company))
            
            conn.commit()
            
            # Update user profile
            self._build_user_profile(user_id)
            
            return keywords
    
    def _extract_keywords(self, content):
        """Extract important keywords from content"""
        content_lower = content.lower()
        
        # Job titles
        titles = ['engineer', 'developer', 'analyst', 'manager', 'designer',
                 'scientist', 'consultant', 'intern', 'coordinator', 'specialist']
        
        # Skills
        skills = ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
                 'machine learning', 'data analysis', 'project management', 'agile',
                 'marketing', 'sales', 'excel', 'powerpoint', 'communication']
        
        # Industries
        industries = ['tech', 'finance', 'healthcare', 'retail', 'consulting',
                     'education', 'manufacturing', 'entertainment']
        
        # Levels
        levels = ['senior', 'junior', 'entry', 'mid', 'lead', 'principal']
        
        found_keywords = {
            'titles': [t for t in titles if t in content_lower],
            'skills': [s for s in skills if s in content_lower],
            'industries': [i for i in industries if i in content_lower],
            'levels': [l for l in levels if l in content_lower]
        }
        
        return found_keywords
    
    def _build_user_profile(self, user_id):
        """Build user profile based on history using ML"""
        history = self.get_user_history(user_id)
        
        if not history:
            return
        
        # Aggregate all keywords from history
        all_titles = []
        all_skills = []
        all_industries = []
        all_levels = []
        
        for entry in history:
            keywords = self._extract_keywords(entry['job_content'] or '')
            all_titles.extend(keywords['titles'])
            all_skills.extend(keywords['skills'])
            all_industries.extend(keywords['industries'])
            all_levels.extend(keywords['levels'])
        
        # Count frequencies (weighted by recency)
        weights = np.linspace(0.5, 1.0, len(history))
        
        title_counter = Counter()
        skill_counter = Counter()
        industry_counter = Counter()
        level_counter = Counter()
        
        for i, entry in enumerate(history):
            keywords = self._extract_keywords(entry['job_content'] or '')
            for title in keywords['titles']:
                title_counter[title] += weights[i]
            for skill in keywords['skills']:
                skill_counter[skill] += weights[i]
            for industry in keywords['industries']:
                industry_counter[industry] += weights[i]
            for level in keywords['levels']:
                level_counter[level] += weights[i]
        
        # Build profile
        profile = {
            'preferred_titles': [t for t, c in title_counter.most_common(5)],
            'preferred_skills': [s for s, c in skill_counter.most_common(10)],
            'preferred_industries': [i for i, c in industry_counter.most_common(3)],
            'preferred_levels': [l for l, c in level_counter.most_common(2)],
            'history_count': len(history)
        }
        
        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences 
                (user_id, preferred_titles, preferred_skills, preferred_industries, preferred_levels, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                json.dumps(profile['preferred_titles']),
                json.dumps(profile['preferred_skills']),
                json.dumps(profile['preferred_industries']),
                json.dumps(profile['preferred_levels'])
            ))
            conn.commit()
        
        return profile
    
    def get_user_profile(self, user_id):
        """Get user profile from database"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT preferred_titles, preferred_skills, preferred_industries, preferred_levels
                FROM user_preferences
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'preferred_titles': json.loads(row['preferred_titles']),
                    'preferred_skills': json.loads(row['preferred_skills']),
                    'preferred_industries': json.loads(row['preferred_industries']),
                    'preferred_levels': json.loads(row['preferred_levels']),
                    'history_count': len(self.get_user_history(user_id))
                }
            
            return None
    
    def get_personalized_recommendations(self, user_id, limit=10, risk_filter='mixed'):
        """Get personalized recommendations for a specific user"""
        # Get extra jobs to ensure we have enough after filtering
        fetch_limit = limit * 3
        
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            recommendations = self._get_default_recommendations(fetch_limit)
        else:
            all_jobs = []
            profile = user_profile
            
            # Search based on user preferences
            for title in profile['preferred_titles'][:3]:
                # Search Indeed
                indeed_jobs = self._search_indeed(title, 'Remote', limit=5)
                all_jobs.extend(indeed_jobs)
                
                # Search Remote OK
                remote_jobs = self._search_remote_ok(title, limit=3)
                all_jobs.extend(remote_jobs)
            
            # Search based on skills
            for skill in profile['preferred_skills'][:2]:
                indeed_jobs = self._search_indeed(skill, 'Remote', limit=3)
                all_jobs.extend(indeed_jobs)
            
            # Remove duplicates
            seen_urls = set()
            unique_jobs = []
            for job in all_jobs:
                if job['url'] not in seen_urls:
                    seen_urls.add(job['url'])
                    unique_jobs.append(job)
            
            # Score using ML-based similarity
            recommendations = self._ml_score_jobs(unique_jobs, user_profile)
            
            # Ensure we have enough jobs
            if len(recommendations) < fetch_limit:
                additional = self._get_additional_jobs(fetch_limit - len(recommendations))
                recommendations.extend(additional)
        
        # Add fraud analysis to each recommendation
        print(f"\n🔍 Analyzing {len(recommendations)} jobs for fraud (User ID: {user_id})...")
        for i, job in enumerate(recommendations):
            fraud_analysis = fraud_detector.quick_analyze(
                job['title'],
                job['company'],
                job.get('description', ''),
                job['url']
            )
            
            job['fraud_analysis'] = fraud_analysis
            job['fraud_score'] = fraud_analysis['fraud_score']
            job['risk_level'] = fraud_analysis['risk_level']
            job['is_safe'] = fraud_analysis['is_safe']
            
            if 'final_score' not in job:
                job['final_score'] = job.get('relevance_score', 0)
        
        # Save recommendations to database
        self._save_recommendations(user_id, recommendations[:limit])
        
        # Apply risk filtering
        filtered_recommendations = self._apply_risk_filter(recommendations, risk_filter, limit)
        
        return filtered_recommendations
    
    def _apply_risk_filter(self, recommendations, risk_filter, limit):
        """Apply risk filtering to recommendations"""
        if risk_filter == 'safe_only':
            filtered_jobs = [j for j in recommendations if j.get('is_safe', False)]
            print(f"🛡 Filtered to {len(filtered_jobs)} safe jobs only")
            return sorted(filtered_jobs, key=lambda x: x.get('final_score', 0), reverse=True)[:limit]
        
        elif risk_filter == 'risky_only':
            filtered_jobs = [j for j in recommendations if not j.get('is_safe', False)]
            print(f"⚠ Filtered to {len(filtered_jobs)} risky jobs only")
            return sorted(filtered_jobs, key=lambda x: x.get('final_score', 0), reverse=True)[:limit]
        
        elif risk_filter == 'all':
            print(f"📊 Showing all {len(recommendations)} jobs (no risk filtering)")
            return sorted(recommendations, key=lambda x: x.get('final_score', 0), reverse=True)[:limit]
        
        else:  # 'mixed' - default: 60% safe, 40% risky
            safe_jobs = [j for j in recommendations if j.get('is_safe', False)]
            risky_jobs = [j for j in recommendations if not j.get('is_safe', False)]
            
            safe_jobs = sorted(safe_jobs, key=lambda x: x.get('final_score', 0), reverse=True)
            risky_jobs = sorted(risky_jobs, key=lambda x: x.get('final_score', 0), reverse=True)
            
            safe_count = int(limit * 0.6)
            risky_count = limit - safe_count
            
            print(f"🔀 Mixed mode: {safe_count} safe + {risky_count} risky jobs")
            
            mixed_recommendations = safe_jobs[:safe_count] + risky_jobs[:risky_count]
            
            if len(mixed_recommendations) < limit:
                remaining = limit - len(mixed_recommendations)
                if len(safe_jobs) > safe_count:
                    mixed_recommendations.extend(safe_jobs[safe_count:safe_count + remaining])
                elif len(risky_jobs) > risky_count:
                    mixed_recommendations.extend(risky_jobs[risky_count:risky_count + remaining])
            
            return mixed_recommendations[:limit]
    
    def _save_recommendations(self, user_id, recommendations):
        """Save recommendations to database"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Clear old recommendations for this user (keep last 100)
            cursor.execute('''
                DELETE FROM job_recommendations 
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM job_recommendations 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 100
                )
            ''', (user_id, user_id))
            
            # Insert new recommendations
            for job in recommendations:
                cursor.execute('''
                    INSERT INTO job_recommendations 
                    (user_id, job_title, job_company, job_location, job_description, job_url, 
                     job_source, fraud_score, risk_level, is_safe, relevance_score, ml_score, final_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    job['title'],
                    job['company'],
                    job.get('location', ''),
                    job.get('description', ''),
                    job['url'],
                    job.get('source', ''),
                    job.get('fraud_score', 0),
                    job.get('risk_level', ''),
                    job.get('is_safe', False),
                    job.get('relevance_score', 0),
                    job.get('ml_score', 0),
                    job.get('final_score', 0)
                ))
            
            conn.commit()
    
    def _ml_score_jobs(self, jobs, user_profile):
        """Score jobs using TF-IDF and cosine similarity"""
        if not user_profile or not jobs:
            return sorted(jobs, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Create user preference text
        user_text = ' '.join(
            user_profile['preferred_titles'] * 3 +
            user_profile['preferred_skills'] * 2 +
            user_profile['preferred_industries']
        )
        
        # Create job texts
        job_texts = []
        for job in jobs:
            job_text = f"{job['title']} {job['company']} {job.get('description', '')}"
            job_texts.append(job_text)
        
        # Calculate TF-IDF similarity
        try:
            all_texts = [user_text] + job_texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            user_vector = tfidf_matrix[0:1]
            job_vectors = tfidf_matrix[1:]
            similarities = cosine_similarity(user_vector, job_vectors)[0]
            
            for i, job in enumerate(jobs):
                ml_score = similarities[i] * 100
                base_score = job.get('relevance_score', 0)
                job['ml_score'] = float(ml_score)
                job['final_score'] = base_score + ml_score
            
            return sorted(jobs, key=lambda x: x['final_score'], reverse=True)
            
        except Exception as e:
            print(f"ML scoring error: {e}")
            return jobs
    
    def _get_default_recommendations(self, limit=10):
        """Get default recommendations when no history exists"""
        jobs = []
        
        default_queries = ['software engineer', 'data analyst', 'product manager', 
                          'designer', 'marketing']
        
        for query in default_queries:
            indeed_jobs = self._search_indeed(query, 'Remote', limit=2)
            jobs.extend(indeed_jobs)
            
            if len(jobs) >= limit:
                break
        
        return jobs[:limit]
    
    def _get_additional_jobs(self, count):
        """Get additional jobs to meet minimum requirement"""
        jobs = []
        
        fallback_queries = ['remote jobs', 'entry level', 'junior developer']
        
        for query in fallback_queries:
            indeed_jobs = self._search_indeed(query, 'Remote', limit=count)
            jobs.extend(indeed_jobs)
            
            if len(jobs) >= count:
                break
        
        return jobs[:count]
    
    def _search_indeed(self, query, location, limit=5):
        """Search Indeed for jobs"""
        jobs = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
                        job_url = urljoin('https://www.indeed.com', link_elem['href']) if link_elem else url
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': loc,
                            'description': description,
                            'source': 'Indeed',
                            'url': job_url,
                            'posted': 'Recently',
                            'type': 'Full-time',
                            'relevance_score': 10
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Indeed search error: {e}")
        
        return jobs
    
    def _search_remote_ok(self, query, limit=3):
        """Search Remote OK for remote jobs"""
        jobs = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = "https://remoteok.com/api"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                query_lower = query.lower()
                filtered_jobs = [job for job in data[1:] if query_lower in job.get('position', '').lower()]
                
                for job in filtered_jobs[:limit]:
                    jobs.append({
                        'title': job.get('position', 'N/A'),
                        'company': job.get('company', 'N/A'),
                        'location': 'Remote',
                        'description': job.get('description', '')[:200],
                        'source': 'Remote OK',
                        'url': job.get('url', 'https://remoteok.com'),
                        'posted': job.get('date', 'Recently'),
                        'type': 'Remote',
                        'tags': job.get('tags', [])[:3],
                        'relevance_score': 10
                    })
                    
        except Exception as e:
            print(f"Remote OK search error: {e}")
        
        return jobs
    
    def get_user_stats(self, user_id):
        """Get user browsing statistics"""
        profile = self.get_user_profile(user_id)
        history = self.get_user_history(user_id)
        
        if not profile:
            return {
                'history_count': 0,
                'message': 'No browsing history yet. Start analyzing jobs to get personalized recommendations!'
            }
        
        return {
            'history_count': len(history),
            'profile': profile,
            'recent_searches': [entry['job_url'] for entry in history[:5]]
        }


# Initialize recommender
recommender = MLJobRecommender()

# Initialize database on startup
init_db()

# ==================== API ENDPOINTS ====================

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user or sync with existing user database"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and email are required'
            }), 400
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email)
                    VALUES (?, ?)
                ''', (data['username'], data['email']))
                
                conn.commit()
                user_id = cursor.lastrowid
                
                return jsonify({
                    'success': True,
                    'message': 'User registered successfully',
                    'user_id': user_id
                })
                
            except sqlite3.IntegrityError:
                # User already exists
                cursor.execute('''
                    SELECT id, username, email FROM users
                    WHERE username = ? OR email = ?
                ''', (data['username'], data['email']))
                
                user = cursor.fetchone()
                
                return jsonify({
                    'success': True,
                    'message': 'User already exists',
                    'user_id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/<username>', methods=['GET'])
def get_user_by_username(username):
    """Get user by username"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, created_at FROM users
                WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            if user:
                return jsonify({
                    'success': True,
                    'user': dict(user)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ml-recommend', methods=['POST'])
def ml_recommend():
    """Get ML-based personalized recommendations for a specific user"""
    try:
        data = request.get_json() or {}
        
        # Get user_id (required)
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        
        # Get parameters
        limit = max(data.get('limit', 10), 10)
        risk_filter = data.get('risk_filter', 'mixed')
        
        print(f"\n{'='*60}")
        print(f"🤖 ML Recommendation Request")
        print(f"   User ID: {user_id}")
        print(f"   Jobs requested: {limit}")
        print(f"   Risk filter: {risk_filter}")
        print(f"{'='*60}")
        
        # Get recommendations
        recommendations = recommender.get_personalized_recommendations(
            user_id=user_id,
            limit=limit,
            risk_filter=risk_filter
        )
        
        # Get user stats
        stats = recommender.get_user_stats(user_id)
        
        # Calculate safety statistics
        safe_jobs = [j for j in recommendations if j.get('is_safe', False)]
        risky_jobs = [j for j in recommendations if not j.get('is_safe', False)]
        
        print(f"\n✅ Safe jobs: {len(safe_jobs)}")
        print(f"⚠  Risky jobs: {len(risky_jobs)}")
        print(f"📊 Total: {len(recommendations)}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'recommendations': recommendations,
            'count': len(recommendations),
            'risk_filter': risk_filter,
            'safety_stats': {
                'safe_count': len(safe_jobs),
                'risky_count': len(risky_jobs),
                'total': len(recommendations)
            },
            'user_stats': stats,
            'ml_powered': True,
            'fraud_checked': True,
            'personalized': stats['history_count'] > 0
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze-and-learn', methods=['POST'])
def analyze_and_learn():
    """Analyze a job URL using external fraud detection API and add it to user history for learning"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data or 'user_id' not in data:
            return jsonify({
                'success': False,
                'error': 'URL and user_id are required'
            }), 400
        
        url = data['url']
        user_id = data['user_id']
        
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        
        print(f"\n📊 Analyzing job: {url} for User ID: {user_id}")
        print(f"🔗 Using external fraud detection API at http://localhost:5000")
        
        # Call external fraud detection API
        try:
            fraud_api_response = requests.post(
                'http://localhost:5000/api/analyze',
                json={'url': url},
                timeout=30
            )
            
            if fraud_api_response.status_code == 200:
                fraud_api_data = fraud_api_response.json()
                
                if fraud_api_data.get('success'):
                    # Extract data from fraud API response
                    title = fraud_api_data.get('job_title', 'Unknown')
                    fraud_score = fraud_api_data.get('fraud_score', 0)
                    verdict = fraud_api_data.get('verdict', 'Unknown')
                    risk_level = fraud_api_data.get('risk_level', 'Unknown')
                    red_flags = fraud_api_data.get('red_flags', [])
                    details = fraud_api_data.get('details', {})
                    
                    # Determine if safe (fraud_score < 40 for medium risk threshold)
                    is_safe = fraud_score < 40
                    
                    print(f"✅ Fraud API Response: {verdict} (Score: {fraud_score})")
                    
                    fraud_analysis = {
                        'fraud_score': fraud_score,
                        'risk_level': risk_level,
                        'verdict': verdict,
                        'red_flags': red_flags,
                        'is_safe': is_safe,
                        'details': details
                    }
                else:
                    raise Exception(f"Fraud API returned error: {fraud_api_data.get('error')}")
            else:
                raise Exception(f"Fraud API returned status code: {fraud_api_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': 'Could not connect to fraud detection API at http://localhost:5000. Make sure it is running.'
            }), 503
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Fraud detection API request timed out'
            }), 504
        except Exception as e:
            print(f"⚠ Fraud API Error: {e}")
            return jsonify({
                'success': False,
                'error': f'Fraud detection API error: {str(e)}'
            }), 500
        
        # Fetch job posting content for ML learning
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company from page
            company_elem = soup.find('div', class_=re.compile('company|employer'))
            company = company_elem.get_text(strip=True) if company_elem else details.get('company_website', 'N/A')
            
            # Extract description
            description_elem = soup.find('div', class_=re.compile('description|content'))
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            content = soup.get_text(separator=' ', strip=True)
            
        except Exception as e:
            print(f"⚠ Warning: Could not fetch full content for ML learning: {e}")
            content = f"{title} {company}"
            description = ""
        
        # Save analyzed job to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO analyzed_jobs 
                (user_id, job_url, job_title, job_company, job_description, 
                 fraud_score, risk_level, verdict, red_flags, is_safe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, url, title, company, description[:500],
                fraud_analysis['fraud_score'],
                fraud_analysis['risk_level'],
                fraud_analysis['verdict'],
                json.dumps(fraud_analysis['red_flags']),
                fraud_analysis['is_safe']
            ))
            conn.commit()
        
        # Add to history for ML learning
        recommender.add_to_history(user_id, url, content, title, company)
        
        history = recommender.get_user_history(user_id)
        print(f"✅ Added to learning history (Total: {len(history)} jobs)")
        
        # Get updated recommendations
        recommendations = recommender.get_personalized_recommendations(
            user_id=user_id,
            limit=10,
            risk_filter='mixed'
        )
        
        # Get user stats
        stats = recommender.get_user_stats(user_id)
        
        # Safety stats
        safe_jobs = [j for j in recommendations if j.get('is_safe', False)]
        
        return jsonify({
            'success': True,
            'message': 'Job analyzed and added to your profile',
            'user_id': user_id,
            'analyzed_job': {
                'title': title,
                'company': company,
                'url': url,
                'fraud_analysis': fraud_analysis
            },
            'recommendations': recommendations,
            'count': len(recommendations),
            'safety_stats': {
                'safe_count': len(safe_jobs),
                'risky_count': len(recommendations) - len(safe_jobs)
            },
            'user_stats': stats,
            'fraud_checked': True,
            'fraud_api_used': True
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user-profile/<int:user_id>', methods=['GET'])
def get_user_profile_api(user_id):
    """Get user's learned profile"""
    try:
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        
        stats = recommender.get_user_stats(user_id)
        
        return jsonify({
            'success': True,
            'user': dict(user),
            'profile': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user-history/<int:user_id>', methods=['GET'])
def get_user_history_api(user_id):
    """Get user's browsing history"""
    try:
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        
        history = recommender.get_user_history(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyzed-jobs/<int:user_id>', methods=['GET'])
def get_analyzed_jobs(user_id):
    """Get all analyzed jobs for a user"""
    try:
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Get analyzed jobs
            cursor.execute('''
                SELECT id, job_url, job_title, job_company, job_description,
                       fraud_score, risk_level, verdict, red_flags, is_safe, analyzed_at
                FROM analyzed_jobs
                WHERE user_id = ?
                ORDER BY analyzed_at DESC
                LIMIT 50
            ''', (user_id,))
            
            jobs = cursor.fetchall()
            
            # Parse red_flags JSON
            results = []
            for job in jobs:
                job_dict = dict(job)
                job_dict['red_flags'] = json.loads(job_dict['red_flags'])
                results.append(job_dict)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'analyzed_jobs': results,
                'count': len(results)
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_saved_recommendations(user_id):
    """Get saved recommendations for a user"""
    try:
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Get recommendations
            cursor.execute('''
                SELECT id, job_title, job_company, job_location, job_description, job_url,
                       job_source, fraud_score, risk_level, is_safe, 
                       relevance_score, ml_score, final_score, created_at
                FROM job_recommendations
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (user_id,))
            
            recommendations = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'recommendations': [dict(row) for row in recommendations],
                'count': len(recommendations)
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clear-history/<int:user_id>', methods=['POST'])
def clear_history(user_id):
    """Clear user history and reset profile"""
    try:
        # Verify user exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Clear history
            cursor.execute('DELETE FROM user_job_history WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM user_preferences WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM job_recommendations WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM analyzed_jobs WHERE user_id = ?', (user_id,))
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'History cleared successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'ML-Powered Job Recommendation API with User Database',
        'version': '3.0',
        'features': [
            'User-specific recommendations',
            'Machine Learning based personalization',
            'Learns from individual browsing history',
            'TF-IDF and Cosine Similarity',
            'Fraud detection and risk scoring',
            'Flexible risk filtering (safe, risky, mixed, all)',
            'SQLite database for persistent storage',
            'Per-user job history and preferences'
        ],
        'endpoints': {
            'POST /api/users/register': 'Register or sync user',
            'GET /api/users/<username>': 'Get user by username',
            'POST /api/analyze-and-learn': 'Analyze job and learn from it (requires user_id)',
            'POST /api/ml-recommend': 'Get ML-based recommendations (requires user_id)',
            'GET /api/user-profile/<user_id>': 'View user learned profile',
            'GET /api/user-history/<user_id>': 'View user browsing history',
            'GET /api/analyzed-jobs/<user_id>': 'View all analyzed jobs',
            'GET /api/recommendations/<user_id>': 'View saved recommendations',
            'POST /api/clear-history/<user_id>': 'Clear user browsing history'
        },
        'risk_filter_options': {
            'mixed': '60% safe + 40% risky jobs (default)',
            'all': 'All jobs regardless of risk',
            'safe_only': 'Only low-risk jobs',
            'risky_only': 'Only high-risk jobs'
        }
    })


if _name_ == '_main_':
    app.run(debug=True, host='0.0.0.0', port=5002)