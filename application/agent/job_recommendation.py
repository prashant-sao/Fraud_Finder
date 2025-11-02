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

app = Flask(__name__)
CORS(app)

# Import fraud detection logic
class JobFraudDetector:
    def __init__(self):
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
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.user_history = []
        self.user_profile = None
        
    def add_to_history(self, url, content):
        """Add analyzed job to user history"""
        self.user_history.append({
            'url': url,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'keywords': self._extract_keywords(content)
        })
        
        # Keep only last 50 entries
        if len(self.user_history) > 50:
            self.user_history = self.user_history[-50:]
        
        # Update user profile
        self._build_user_profile()
    
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
    
    def _build_user_profile(self):
        """Build user profile based on history using ML"""
        if not self.user_history:
            return
        
        # Aggregate all keywords from history
        all_titles = []
        all_skills = []
        all_industries = []
        all_levels = []
        
        for entry in self.user_history:
            keywords = entry['keywords']
            all_titles.extend(keywords['titles'])
            all_skills.extend(keywords['skills'])
            all_industries.extend(keywords['industries'])
            all_levels.extend(keywords['levels'])
        
        # Count frequencies (weighted by recency)
        weights = np.linspace(0.5, 1.0, len(self.user_history))
        
        title_counter = Counter()
        skill_counter = Counter()
        industry_counter = Counter()
        level_counter = Counter()
        
        for i, entry in enumerate(self.user_history):
            keywords = entry['keywords']
            for title in keywords['titles']:
                title_counter[title] += weights[i]
            for skill in keywords['skills']:
                skill_counter[skill] += weights[i]
            for industry in keywords['industries']:
                industry_counter[industry] += weights[i]
            for level in keywords['levels']:
                level_counter[level] += weights[i]
        
        # Build profile
        self.user_profile = {
            'preferred_titles': [t for t, c in title_counter.most_common(5)],
            'preferred_skills': [s for s, c in skill_counter.most_common(10)],
            'preferred_industries': [i for i, c in industry_counter.most_common(3)],
            'preferred_levels': [l for l, c in level_counter.most_common(2)],
            'history_count': len(self.user_history)
        }
    
    def get_personalized_recommendations(self, limit=10):
        """Get personalized recommendations based on user history"""
        if not self.user_profile:
            recommendations = self._get_default_recommendations(limit)
        else:
            all_jobs = []
            profile = self.user_profile
            
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
            recommendations = self._ml_score_jobs(unique_jobs)
            
            # Ensure minimum 10 recommendations
            if len(recommendations) < limit:
                # Add more jobs from different sources
                additional = self._get_additional_jobs(limit - len(recommendations))
                recommendations.extend(additional)
        
        # Add fraud analysis to each recommendation
        print(f"\n🔍 Analyzing {len(recommendations)} jobs for fraud...")
        for i, job in enumerate(recommendations[:limit]):
            print(f"Analyzing job {i+1}/{min(len(recommendations), limit)}: {job['title']}")
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
            
            # Adjust final score based on safety
            if fraud_analysis['fraud_score'] > 50:
                job['final_score'] = job.get('final_score', 0) * 0.5  # Penalize risky jobs
        
        # Sort by final score (preferring safe jobs)
        recommendations = sorted(recommendations, key=lambda x: (x.get('is_safe', False), x.get('final_score', 0)), reverse=True)
        
        return recommendations[:limit]
    
    def _ml_score_jobs(self, jobs):
        """Score jobs using TF-IDF and cosine similarity"""
        if not self.user_profile or not jobs:
            return sorted(jobs, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Create user preference text
        user_text = ' '.join(
            self.user_profile['preferred_titles'] * 3 +  # Weight titles higher
            self.user_profile['preferred_skills'] * 2 +
            self.user_profile['preferred_industries']
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
            
            # Calculate cosine similarity
            user_vector = tfidf_matrix[0:1]
            job_vectors = tfidf_matrix[1:]
            similarities = cosine_similarity(user_vector, job_vectors)[0]
            
            # Add ML score to jobs
            for i, job in enumerate(jobs):
                ml_score = similarities[i] * 100
                base_score = job.get('relevance_score', 0)
                job['ml_score'] = float(ml_score)
                job['final_score'] = base_score + ml_score
            
            # Sort by final score
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
    
    def get_user_stats(self):
        """Get user browsing statistics"""
        if not self.user_profile:
            return {
                'history_count': 0,
                'message': 'No browsing history yet. Start analyzing jobs to get personalized recommendations!'
            }
        
        return {
            'history_count': len(self.user_history),
            'profile': self.user_profile,
            'recent_searches': [entry['url'] for entry in self.user_history[-5:]]
        }


# Initialize recommender
recommender = MLJobRecommender()

@app.route('/api/ml-recommend', methods=['POST'])
def ml_recommend():
    """Get ML-based personalized recommendations with fraud scores"""
    try:
        data = request.get_json()
        
        # Get limit (default 10, minimum 10)
        limit = max(data.get('limit', 10), 10)
        
        print(f"\n{'='*60}")
        print(f"🤖 ML Recommendation Request - Getting {limit} jobs")
        print(f"{'='*60}")
        
        # Get recommendations based on history
        recommendations = recommender.get_personalized_recommendations(limit=limit)
        
        # Get user stats
        stats = recommender.get_user_stats()
        
        # Calculate safety statistics
        safe_jobs = [j for j in recommendations if j.get('is_safe', False)]
        risky_jobs = [j for j in recommendations if not j.get('is_safe', False)]
        
        print(f"\n✅ Safe jobs: {len(safe_jobs)}")
        print(f"⚠️  Risky jobs: {len(risky_jobs)}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations),
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
    """Analyze a job URL and add it to user history for learning"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url']
        
        print(f"\n📊 Analyzing job: {url}")
        
        # Fetch job posting
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.get_text(separator=' ', strip=True)
        
        # Add to history
        recommender.add_to_history(url, content)
        
        print(f"✅ Added to learning history (Total: {len(recommender.user_history)} jobs)")
        
        # Get updated recommendations with fraud scores
        recommendations = recommender.get_personalized_recommendations(limit=10)
        
        # Get user stats
        stats = recommender.get_user_stats()
        
        # Safety stats
        safe_jobs = [j for j in recommendations if j.get('is_safe', False)]
        
        return jsonify({
            'success': True,
            'message': 'Job analyzed and added to your profile',
            'recommendations': recommendations,
            'count': len(recommendations),
            'safety_stats': {
                'safe_count': len(safe_jobs),
                'risky_count': len(recommendations) - len(safe_jobs)
            },
            'user_stats': stats,
            'fraud_checked': True
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user-profile', methods=['GET'])
def get_user_profile():
    """Get user's learned profile"""
    try:
        stats = recommender.get_user_stats()
        
        return jsonify({
            'success': True,
            'profile': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear user history and reset profile"""
    try:
        recommender.user_history = []
        recommender.user_profile = None
        
        return jsonify({
            'success': True,
            'message': 'History cleared successfully'
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
        'service': 'ML-Powered Job Recommendation API',
        'version': '2.0',
        'features': [
            'Machine Learning based recommendations',
            'Learns from your browsing history',
            'TF-IDF and Cosine Similarity',
            'Minimum 10 recommendations guaranteed',
            'Personalized job matching'
        ],
        'endpoints': {
            'POST /api/analyze-and-learn': 'Analyze job and learn from it',
            'POST /api/ml-recommend': 'Get ML-based recommendations',
            'GET /api/user-profile': 'View your learned profile',
            'POST /api/clear-history': 'Clear browsing history'
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)