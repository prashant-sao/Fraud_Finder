import logging
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, urljoin
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Import local fraud detector if available; fallback to None
try:
    from application.agent.risk_score import JobFraudDetector
    fraud_detector = JobFraudDetector()
except Exception:
    fraud_detector = None
    logger.warning("fraud_detector not available; fraud analysis will be skipped.")

# Import database and models
try:
    from application.database import db
    from application.models import User
except Exception:
    db = None
    User = None
    logger.warning("Database models not available; personalization will be limited.")


class MLJobRecommender:
    """Personalized job recommender with fraud analysis and alert formatting."""

    def __init__(self):
        self.alert_templates = {
            'phishing': {
                'title': 'Phishing Scam Alert',
                'category': 'Email',
                'description': 'This job posting contains suspicious elements commonly found in phishing scams. Be cautious of requests for personal information or account details.'
            },
            'investment_fraud': {
                'title': 'Investment Fraud Scheme',
                'category': 'Social Media',
                'description': 'Fraudsters are promoting fake job opportunities that require upfront investment. Be wary of positions guaranteeing unrealistic returns.'
            },
            'fake_company': {
                'title': 'Fake Company Alert',
                'category': 'Website',
                'description': 'This job posting may be from a fraudulent company with no legitimate business presence. Verify company details before applying.'
            },
            'payment_scam': {
                'title': 'Payment Processing Scam',
                'category': 'Email',
                'description': 'This position involves suspicious payment processing activities that may be part of a money laundering scheme.'
            },
            'data_harvesting': {
                'title': 'Data Harvesting Alert',
                'category': 'Website',
                'description': 'This job posting may be collecting personal information for fraudulent purposes. Avoid sharing sensitive details.'
            },
            'low_risk': {
                'title': 'Verified Job Opportunity',
                'category': 'Website',
                'description': 'This job posting appears legitimate based on our analysis. However, always verify company details independently.'
            }
        }

    def get_recommendations(self, limit=10, search_query=None, user_id=None):
        """
        Get personalized job recommendations with fraud analysis.
        
        Args:
            limit (int): Number of jobs to return
            search_query (str|None): Optional search terms
            user_id (int|None): User ID for personalization
        
        Returns:
            list[dict]: List of job recommendations with fraud analysis
        """
        # If user_id provided, get personalized recommendations
        if user_id and User and db:
            return self._get_personalized_recommendations(user_id, limit)
        
        # Otherwise, return generic recommendations
        return self._get_generic_recommendations(limit, search_query)
    
    def _get_personalized_recommendations(self, user_id, limit=10):
        """Get personalized recommendations based on user profile"""
        try:
            # Import models here to avoid circular imports
            from application.models import User_Job_Alerts, User_Alert_Preferences
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return []
            
            # Get or create user preferences
            preferences = User_Alert_Preferences.query.filter_by(user_id=user_id).first()
            if not preferences:
                preferences = User_Alert_Preferences(
                    user_id=user_id,
                    viewed_job_ids=json.dumps([])
                )
                db.session.add(preferences)
                db.session.commit()
            
            # Get viewed job IDs
            viewed_jobs = json.loads(preferences.viewed_job_ids) if preferences.viewed_job_ids else []
            
            # Get search terms based on user profile
            search_terms = self._get_user_search_terms(user)
            
            # Fetch jobs
            all_jobs = []
            for query in search_terms[:3]:
                try:
                    indeed_jobs = self._search_indeed(query, "Remote", limit=5)
                    all_jobs.extend(indeed_jobs)
                except Exception as e:
                    logger.error(f"Indeed search failed for '{query}': {e}")
                
                try:
                    remote_jobs = self._search_remote_ok(query, limit=3)
                    all_jobs.extend(remote_jobs)
                except Exception as e:
                    logger.error(f"RemoteOK search failed for '{query}': {e}")
                
                if len(all_jobs) >= limit * 3:
                    break
            
            # Remove duplicates and already viewed jobs
            seen_urls = set(viewed_jobs)
            unique_jobs = []
            for job in all_jobs:
                job_hash = self._hash_job(job['url'], job['title'])
                if job_hash not in seen_urls:
                    seen_urls.add(job_hash)
                    unique_jobs.append(job)
            
            # Add fraud analysis and create alerts
            alerts = []
            for job in unique_jobs:
                alert_data = self._analyze_and_create_alert(job)
                alerts.append(alert_data)
            
            # Get mixed recommendations (60% safe, 40% risky)
            mixed_alerts = self._get_mixed_recommendations(alerts, limit)
            
            # Save alerts to database
            saved_alerts = []
            for alert_data in mixed_alerts:
                alert = User_Job_Alerts(
                    user_id=user_id,
                    alert_title=alert_data['title'],
                    alert_subtitle=alert_data['subtitle'],
                    alert_description=alert_data['description'],
                    risk_level=alert_data['risk_level'],
                    risk_category=alert_data['risk_category'],
                    fraud_score=alert_data['fraud_score'],
                    job_title=alert_data['job_title'],
                    job_company=alert_data['job_company'],
                    job_url=alert_data['job_url'],
                    job_source=alert_data.get('source', 'Unknown')
                )
                db.session.add(alert)
                saved_alerts.append(alert)
            
            db.session.commit()
            
            # Update viewed jobs
            new_viewed = viewed_jobs + [self._hash_job(a['job_url'], a['job_title']) for a in mixed_alerts]
            preferences.viewed_job_ids = json.dumps(new_viewed[-200:])  # Keep last 200
            preferences.last_updated = datetime.utcnow()
            db.session.commit()
            
            # Return formatted alerts
            return [alert.to_dict() for alert in saved_alerts]
            
        except Exception as e:
            logger.error(f"Personalized recommendations error: {e}")
            if db:
                db.session.rollback()
            return self._get_generic_recommendations(limit, None)
    
    def _get_generic_recommendations(self, limit=10, search_query=None):
        """Get generic recommendations (fallback when no user_id)"""
        # Determine search terms
        if search_query:
            search_terms = [search_query]
        else:
            search_terms = [
                "software engineer", "data analyst", "product manager",
                "designer", "marketing", "developer"
            ]
        
        # Fetch jobs
        all_jobs = []
        for query in search_terms[:3]:
            try:
                indeed_jobs = self._search_indeed(query, "Remote", limit=5)
                all_jobs.extend(indeed_jobs)
            except Exception as e:
                logger.error(f"Indeed search failed: {e}")
            
            try:
                remote_jobs = self._search_remote_ok(query, limit=3)
                all_jobs.extend(remote_jobs)
            except Exception as e:
                logger.error(f"RemoteOK search failed: {e}")
            
            if len(all_jobs) >= limit * 2:
                break
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        # Add fraud analysis
        if fraud_detector:
            for job in unique_jobs:
                try:
                    fraud_analysis = fraud_detector.quick_analyze(
                        job.get("title", ""),
                        job.get("company", ""),
                        job.get("description", ""),
                        job.get("url", "")
                    )
                    job["fraud_analysis"] = fraud_analysis
                    job["fraud_score"] = fraud_analysis.get("fraud_score", 0)
                    job["risk_level"] = fraud_analysis.get("risk_level", "Unknown")
                    job["is_safe"] = fraud_analysis.get("is_safe", True)
                    job["verdict"] = fraud_analysis.get("verdict", "Unknown")
                    job["red_flags"] = fraud_analysis.get("red_flags", [])
                except Exception as e:
                    logger.error(f"Fraud analysis failed: {e}")
                    job["fraud_score"] = 0
                    job["is_safe"] = True
        
        # Return mixed recommendations
        return self._get_mixed_recommendations(unique_jobs, limit)
    
    def _get_user_search_terms(self, user):
        """Generate search terms based on user profile"""
        search_terms = []
        
        # Use user's fields of interest
        if user.fields_of_interest:
            interests = [i.strip() for i in user.fields_of_interest.split(',')]
            search_terms.extend(interests[:3])
        
        # Use user's qualifications
        if user.qualifications:
            search_terms.append(user.qualifications)
        
        # Default if no user data
        if not search_terms:
            search_terms = ['software engineer', 'data analyst', 'developer']
        
        return search_terms
    
    def _analyze_and_create_alert(self, job):
        """Analyze job and create alert-style result"""
        if not fraud_detector:
            return self._create_simple_alert(job)
        
        try:
            fraud_analysis = fraud_detector.quick_analyze(
                job.get("title", ""),
                job.get("company", ""),
                job.get("description", ""),
                job.get("url", "")
            )
            
            fraud_score = fraud_analysis.get("fraud_score", 0)
            is_safe = fraud_analysis.get("is_safe", True)
            
            # Determine alert type
            if fraud_score >= 60:
                if 'email' in str(fraud_analysis.get('red_flags', [])).lower():
                    alert_type = 'phishing'
                elif 'salary' in str(fraud_analysis.get('red_flags', [])).lower():
                    alert_type = 'investment_fraud'
                else:
                    alert_type = 'fake_company'
            elif fraud_score >= 30:
                alert_type = 'payment_scam'
            else:
                alert_type = 'low_risk'
            
            template = self.alert_templates.get(alert_type, self.alert_templates['fake_company'])
            
            return {
                'title': template['title'],
                'subtitle': f"{job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}",
                'description': template['description'],
                'risk_level': fraud_analysis.get('risk_level', 'Unknown'),
                'risk_category': template['category'],
                'fraud_score': fraud_score,
                'is_safe': is_safe,
                'job_title': job.get('title', ''),
                'job_company': job.get('company', ''),
                'job_url': job.get('url', ''),
                'source': job.get('source', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Alert creation failed: {e}")
            return self._create_simple_alert(job)
    
    def _create_simple_alert(self, job):
        """Create simple alert without fraud analysis"""
        template = self.alert_templates['low_risk']
        return {
            'title': template['title'],
            'subtitle': f"{job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}",
            'description': template['description'],
            'risk_level': 'Low Risk',
            'risk_category': template['category'],
            'fraud_score': 0,
            'is_safe': True,
            'job_title': job.get('title', ''),
            'job_company': job.get('company', ''),
            'job_url': job.get('url', ''),
            'source': job.get('source', 'Unknown')
        }
    
    def _hash_job(self, url, title):
        """Create unique hash for job tracking"""
        content = f"{url}{title}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_mixed_recommendations(self, jobs, limit):
        """Return mixed recommendations: 60% safe, 40% risky"""
        safe_jobs = [j for j in jobs if j.get("is_safe", False)]
        risky_jobs = [j for j in jobs if not j.get("is_safe", False)]
        
        safe_count = int(limit * 0.6)
        risky_count = limit - safe_count
        
        logger.info(f"Mixed recommendations: {safe_count} safe + {risky_count} risky jobs")
        
        mixed = safe_jobs[:safe_count] + risky_jobs[:risky_count]
        
        # Fill remaining slots
        if len(mixed) < limit:
            remaining = limit - len(mixed)
            if len(safe_jobs) > safe_count:
                mixed.extend(safe_jobs[safe_count:safe_count + remaining])
            elif len(risky_jobs) > risky_count:
                mixed.extend(risky_jobs[risky_count:risky_count + remaining])
        
        return mixed[:limit]
    
    def _search_indeed(self, query, location, limit=5):
        """Scrape basic job info from Indeed"""
        jobs = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            job_cards = soup.find_all("div", class_=re.compile("job_seen_beacon|jobsearch-SerpJobCard"))
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find("h2", class_="jobTitle")
                    company_elem = card.find("span", class_="companyName")
                    location_elem = card.find("div", class_="companyLocation")
                    snippet_elem = card.find("div", class_="job-snippet")
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        loc = location_elem.get_text(strip=True) if location_elem else location
                        description = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        link_elem = card.find("a", class_="jcs-JobTitle")
                        job_url = urljoin("https://www.indeed.com", link_elem["href"]) if link_elem and link_elem.get("href") else url
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "description": description,
                            "source": "Indeed",
                            "url": job_url,
                            "posted": "Recently",
                            "type": "Full-time"
                        })
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Indeed search error: {e}")
        return jobs
    
    def _search_remote_ok(self, query, limit=3):
        """Use RemoteOK public API"""
        jobs = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            url = "https://remoteok.com/api"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            query_lower = query.lower()
            filtered = [job for job in data[1:] if query_lower in job.get("position", "").lower()]
            for job in filtered[:limit]:
                jobs.append({
                    "title": job.get("position", "N/A"),
                    "company": job.get("company", "N/A"),
                    "location": "Remote",
                    "description": (job.get("description", "") or "")[:200],
                    "source": "Remote OK",
                    "url": job.get("url", "https://remoteok.com"),
                    "posted": job.get("date", "Recently"),
                    "type": "Remote",
                    "tags": job.get("tags", [])[:3]
                })
        except Exception as e:
            logger.error(f"Remote OK search error: {e}")
        return jobs


# Global instance
ml_recommender = MLJobRecommender()