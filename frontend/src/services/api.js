import axios from 'axios';

// Force HTTPS for production, allow HTTP for localhost
let API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Force HTTPS if the URL contains domainping.fly.dev but uses HTTP
if (API_BASE_URL.includes('domainping.fly.dev') && API_BASE_URL.startsWith('http://')) {
  API_BASE_URL = API_BASE_URL.replace('http://', 'https://');
  console.warn('Forced HTTPS for Fly.io backend:', API_BASE_URL);
}

// Debug logging
console.log('API Configuration:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  API_BASE_URL: API_BASE_URL,
  NODE_ENV: process.env.NODE_ENV
});

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Domain API
export const domainAPI = {
  // Get all domains
  getDomains: (params = {}) => api.get('/domains/', { params }),
  
  // Get domain by ID
  getDomain: (id) => api.get(`/domains/${id}/`),
  
  // Create new domain
  createDomain: (data) => api.post('/domains/', data),
  
  // Update domain
  updateDomain: (id, data) => api.put(`/domains/${id}/`, data),
  
  // Delete domain
  deleteDomain: (id) => api.delete(`/domains/${id}/`),
  
  // Refresh WHOIS data
  refreshWhois: (id) => api.post(`/domains/${id}/refresh-whois/`),
  
  // Get domain statistics
  getStatistics: () => api.get('/domains/statistics/'),
  
  // Get expiring domains
  getExpiringDomains: (daysAhead = 90) => api.get('/domains/expiring/', { 
    params: { days_ahead: daysAhead } 
  }),
};

// Notification API
export const notificationAPI = {
  // Test email configuration
  testEmail: (email) => api.post('/notifications/test-email/', { email }),
  
  // Test SMS configuration
  testSMS: (phone) => api.post('/notifications/test-sms/', { phone }),
  
  // Test desktop notification
  testDesktop: () => api.post('/notifications/test-desktop/'),
};

export default api; 