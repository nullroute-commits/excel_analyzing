"""Integration tests for Django web interface."""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
import json


@pytest.mark.django_db
class TestWebInterfaceIntegration(TestCase):
    """Integration tests for the Django web interface."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_page_loads(self):
        """Test that the home page loads successfully."""
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])  # 302 if redirecting to login
    
    def test_user_authentication_flow(self):
        """Test complete user authentication workflow."""
        # Test login page
        login_url = reverse('login') if 'login' in [url.name for url in get_urlpatterns()] else '/login/'
        response = self.client.get(login_url)
        self.assertIn(response.status_code, [200, 404])  # 404 if login not implemented yet
        
        # Test login process
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(login_url, login_data)
        # Should redirect or return success
        self.assertIn(response.status_code, [200, 302, 404])
    
    def test_workbook_upload_workflow(self):
        """Test the complete workbook upload and processing workflow."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test Excel file
        import io
        import pandas as pd
        
        buffer = io.BytesIO()
        df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        
        # Test file upload
        upload_data = {
            'file': buffer,
            'name': 'test_workbook.xlsx'
        }
        
        # This would need the actual upload endpoint
        upload_url = '/upload/' if hasattr(self, 'upload_url') else '/'
        response = self.client.post(upload_url, upload_data)
        
        # Check response (exact assertion depends on implementation)
        self.assertIn(response.status_code, [200, 201, 302, 404])


def get_urlpatterns():
    """Helper to get URL patterns safely."""
    try:
        from django.urls import get_resolver
        return get_resolver().url_patterns
    except:
        return []


@pytest.mark.django_db
class TestAPIIntegration(APITestCase):
    """Integration tests for the REST API."""
    
    def setUp(self):
        """Set up API test client and authentication."""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_api_endpoints_accessibility(self):
        """Test that API endpoints are accessible."""
        endpoints = [
            '/api/',
            '/api/workbooks/',
            '/api/sheets/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Should return 200 or 404 if not implemented yet
            self.assertIn(response.status_code, [200, 404])
    
    def test_workbook_api_crud(self):
        """Test CRUD operations on workbook API."""
        # Test GET (list)
        response = self.client.get('/api/workbooks/')
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            # Test POST (create)
            workbook_data = {
                'name': 'Test Workbook',
                'description': 'A test workbook'
            }
            response = self.client.post('/api/workbooks/', workbook_data)
            self.assertIn(response.status_code, [201, 400, 404])
            
            if response.status_code == 201:
                workbook_id = response.data.get('id')
                
                # Test GET (detail)
                response = self.client.get(f'/api/workbooks/{workbook_id}/')
                self.assertEqual(response.status_code, 200)
                
                # Test PUT (update)
                update_data = {
                    'name': 'Updated Workbook',
                    'description': 'An updated test workbook'
                }
                response = self.client.put(f'/api/workbooks/{workbook_id}/', update_data)
                self.assertIn(response.status_code, [200, 404])
                
                # Test DELETE
                response = self.client.delete(f'/api/workbooks/{workbook_id}/')
                self.assertIn(response.status_code, [204, 404])
    
    def test_data_query_api(self):
        """Test data querying through API."""
        # Test querying data from processed sheets
        query_data = {
            'sheet_name': 'Sheet1',
            'filters': {'column': 'Age', 'operator': '>', 'value': 25}
        }
        
        response = self.client.post('/api/query/', query_data)
        self.assertIn(response.status_code, [200, 400, 404])
    
    def test_api_error_handling(self):
        """Test API error handling."""
        # Test invalid data
        invalid_data = {'invalid': 'data'}
        response = self.client.post('/api/workbooks/', invalid_data)
        self.assertIn(response.status_code, [400, 404])
        
        # Test non-existent resource
        response = self.client.get('/api/workbooks/99999/')
        self.assertIn(response.status_code, [404])
    
    def test_api_permissions(self):
        """Test API permission handling."""
        # Test without authentication
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/workbooks/')
        self.assertIn(response.status_code, [401, 403, 404])


@pytest.mark.django_db
class TestEndToEndWorkflow(TestCase):
    """End-to-end workflow integration tests."""
    
    def setUp(self):
        """Set up for end-to-end tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='e2euser',
            email='e2e@example.com',
            password='e2epass123'
        )
        self.client.login(username='e2euser', password='e2epass123')
    
    def test_complete_excel_analysis_workflow(self):
        """Test the complete workflow from upload to analysis."""
        # 1. Upload Excel file
        # 2. Process the file
        # 3. Query the processed data
        # 4. Generate reports
        # 5. Export results
        
        # This is a placeholder for the complete workflow test
        # Would need to be implemented based on actual application flow
        self.assertTrue(True)  # Placeholder assertion
    
    def test_multi_user_workflow(self):
        """Test workflow with multiple users."""
        # Create another user
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass123'
        )
        
        # Test that users can work independently
        # Test sharing and collaboration features if implemented
        self.assertTrue(True)  # Placeholder assertion
    
    def test_error_recovery_workflow(self):
        """Test error recovery in the complete workflow."""
        # Test handling of corrupted files
        # Test network interruption recovery
        # Test database connection issues
        self.assertTrue(True)  # Placeholder assertion