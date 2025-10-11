const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
    async request(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            credentials: 'include',
            ...options,
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    async register(userData) {
        return this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async login(credentials) {
        return this.request('/login', {
            method: 'POST',
        body: JSON.stringify({
            email: credentials.email,  // Changed from username to email
            password: credentials.password,
        }),
        });
    }

    async editProfile(userData) {
        return this.request('/edit_profile', {
            method: 'PUT',
            body: JSON.stringify(userData),
        });
    }

    // Job Analysis
    async analyzeJob(jobData) {
        return this.request('/analyze', {
            method: 'POST',
            body: JSON.stringify(jobData),
        });
    }

    // Reporting
    async reportScam(scamData) {
        return this.request('/report_scam', {
            method: 'POST',
            body: JSON.stringify(scamData),
        });
    }

    // Statistics
    async getStats() {
        return this.request('/stats', {
            method: 'GET',
        });
    }

    async getRecentAlerts() {
        return this.request('/recent_alerts', {
            method: 'GET',
        });
    }
}

export default new ApiService();