import unittest
import os
import tempfile
from app import app, check_single_url, URLS_TO_MONITOR

class TestURLChecker(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        """Test the home page returns 200"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'URL Status Checker', response.data)
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'healthy', response.data)
    
    def test_urls_endpoint(self):
        """Test URLs list endpoint"""
        response = self.app.get('/api/urls')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('monitored_urls', data)
        self.assertIn('total_urls', data)
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = self.app.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
    
    def test_check_single_url_success(self):
        """Test checking a single URL that should work"""
        result = check_single_url('https://httpstat.us/200')
        self.assertIn('status_code', result)
        self.assertIn('response_time', result)
        self.assertIn('success', result)
    
    def test_check_endpoint(self):
        """Test the main check endpoint"""
        response = self.app.get('/api/check')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('summary', data)
        self.assertIn('results', data)
        self.assertIn('timestamp', data)
    
    def test_history_endpoint(self):
        """Test history endpoint"""
        response = self.app.get('/api/history')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('recent_checks', data)
        self.assertIn('total_checks', data)
    
    def test_api_info_endpoint(self):
        """Test API info endpoint"""
        response = self.app.get('/api')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('endpoints', data)
        self.assertIn('status', data)
    
    def test_invalid_route_404(self):
        """Test invalid route returns 404"""
        response = self.app.get('/invalid-route')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)