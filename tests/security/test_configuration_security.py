"""Configuration Security Tests - Test security-related configuration settings."""

import pytest
import os
from django.test import TestCase
from django.conf import settings


class TestProductionSecurityConfiguration(TestCase):
    """Test production security configuration."""
    
    def test_debug_mode_production(self):
        """Test that DEBUG is False in production."""
        if os.environ.get('ENVIRONMENT') == 'production':
            self.assertFalse(settings.DEBUG, "DEBUG must be False in production")
        elif os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('.production'):
            self.assertFalse(settings.DEBUG, "DEBUG must be False in production settings")
    
    def test_allowed_hosts_configuration(self):
        """Test ALLOWED_HOSTS security."""
        # In production, should not allow all hosts
        if os.environ.get('ENVIRONMENT') == 'production':
            self.assertNotIn('*', settings.ALLOWED_HOSTS, 
                           "ALLOWED_HOSTS should not contain wildcard in production")
            self.assertNotEqual(settings.ALLOWED_HOSTS, [], 
                              "ALLOWED_HOSTS should be configured in production")
    
    def test_secret_key_strength(self):
        """Test SECRET_KEY security requirements."""
        secret_key = settings.SECRET_KEY
        
        # Minimum length requirement
        self.assertGreaterEqual(len(secret_key), 50, 
                               "SECRET_KEY should be at least 50 characters")
        
        # Should not be default Django keys
        insecure_patterns = [
            'django-insecure-',
            'your-secret-key-here',
            'change-me',
            'secret',
            'password',
            '1234567890',
            'abcdefgh'
        ]
        
        for pattern in insecure_patterns:
            self.assertNotIn(pattern.lower(), secret_key.lower(), 
                           f"SECRET_KEY contains insecure pattern: {pattern}")
    
    def test_security_middleware(self):
        """Test that security middleware is properly configured."""
        middleware = settings.MIDDLEWARE
        
        # Important security middleware
        security_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ]
        
        for mw in security_middleware:
            self.assertIn(mw, middleware, f"Missing security middleware: {mw}")
    
    def test_session_security_settings(self):
        """Test session security configuration."""
        # Session cookie security
        if os.environ.get('ENVIRONMENT') == 'production':
            # In production, session cookies should be secure
            self.assertTrue(getattr(settings, 'SESSION_COOKIE_SECURE', False),
                          "SESSION_COOKIE_SECURE should be True in production")
            self.assertTrue(getattr(settings, 'SESSION_COOKIE_HTTPONLY', False),
                          "SESSION_COOKIE_HTTPONLY should be True")
        
        # Session timeout should be reasonable
        session_age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)  # 2 weeks default
        self.assertLessEqual(session_age, 86400 * 30,  # 30 days max
                           "Session timeout should not exceed 30 days")
    
    def test_csrf_protection_settings(self):
        """Test CSRF protection configuration."""
        # CSRF cookie settings
        if os.environ.get('ENVIRONMENT') == 'production':
            self.assertTrue(getattr(settings, 'CSRF_COOKIE_SECURE', False),
                          "CSRF_COOKIE_SECURE should be True in production")
            self.assertTrue(getattr(settings, 'CSRF_COOKIE_HTTPONLY', False),
                          "CSRF_COOKIE_HTTPONLY should be True")
    
    def test_https_security_settings(self):
        """Test HTTPS security configuration."""
        if os.environ.get('ENVIRONMENT') == 'production':
            # HTTPS enforcement
            self.assertTrue(getattr(settings, 'SECURE_SSL_REDIRECT', False),
                          "SECURE_SSL_REDIRECT should be True in production")
            
            # HSTS settings
            hsts_seconds = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
            self.assertGreater(hsts_seconds, 0,
                             "SECURE_HSTS_SECONDS should be set in production")
            
            # Secure proxy SSL header
            ssl_header = getattr(settings, 'SECURE_PROXY_SSL_HEADER', None)
            if ssl_header:
                self.assertIsInstance(ssl_header, tuple,
                                    "SECURE_PROXY_SSL_HEADER should be a tuple")
                self.assertEqual(len(ssl_header), 2,
                               "SECURE_PROXY_SSL_HEADER should have 2 elements")


class TestDatabaseSecurityConfiguration(TestCase):
    """Test database security configuration."""
    
    def test_database_credentials_security(self):
        """Test database credential security."""
        for db_name, db_config in settings.DATABASES.items():
            # Password should not be empty or default
            password = db_config.get('PASSWORD', '')
            if password:
                self.assertNotIn(password.lower(), ['password', 'admin', '123456', 'root'],
                               f"Database {db_name} uses weak password")
            
            # Host should not be default insecure values
            host = db_config.get('HOST', '')
            if host:
                insecure_hosts = ['0.0.0.0', '*']
                self.assertNotIn(host, insecure_hosts,
                               f"Database {db_name} uses insecure host: {host}")
    
    def test_database_ssl_configuration(self):
        """Test database SSL configuration."""
        for db_name, db_config in settings.DATABASES.items():
            # In production, PostgreSQL should use SSL
            if (os.environ.get('ENVIRONMENT') == 'production' and 
                db_config.get('ENGINE') == 'django.db.backends.postgresql'):
                
                options = db_config.get('OPTIONS', {})
                sslmode = options.get('sslmode', '')
                
                if sslmode:
                    secure_ssl_modes = ['require', 'verify-ca', 'verify-full']
                    self.assertIn(sslmode, secure_ssl_modes,
                                f"Database {db_name} should use secure SSL mode")


class TestSecurityHeaders(TestCase):
    """Test HTTP security headers configuration."""
    
    def test_security_headers_settings(self):
        """Test security headers configuration."""
        # X-Frame-Options
        frame_options = getattr(settings, 'X_FRAME_OPTIONS', 'DENY')
        self.assertIn(frame_options, ['DENY', 'SAMEORIGIN'],
                     "X_FRAME_OPTIONS should be DENY or SAMEORIGIN")
        
        # Content Type Options
        if hasattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF'):
            self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF,
                          "SECURE_CONTENT_TYPE_NOSNIFF should be True")
        
        # Browser XSS Filter
        if hasattr(settings, 'SECURE_BROWSER_XSS_FILTER'):
            self.assertTrue(settings.SECURE_BROWSER_XSS_FILTER,
                          "SECURE_BROWSER_XSS_FILTER should be True")


class TestLoggingSecurityConfiguration(TestCase):
    """Test logging security configuration."""
    
    def test_logging_configuration_security(self):
        """Test that logging doesn't expose sensitive information."""
        if hasattr(settings, 'LOGGING'):
            logging_config = settings.LOGGING
            
            # Check formatters don't include sensitive data
            formatters = logging_config.get('formatters', {})
            for formatter_name, formatter_config in formatters.items():
                format_str = formatter_config.get('format', '')
                
                # Should not log sensitive information
                sensitive_patterns = ['password', 'secret', 'key', 'token']
                for pattern in sensitive_patterns:
                    self.assertNotIn(pattern.lower(), format_str.lower(),
                                   f"Logging formatter {formatter_name} may expose sensitive data")


class TestEnvironmentVariablesSecurity(TestCase):
    """Test environment variables security."""
    
    def test_required_environment_variables(self):
        """Test that required environment variables are set."""
        # Critical environment variables that should be set
        critical_vars = ['SECRET_KEY']
        
        for var in critical_vars:
            self.assertTrue(os.environ.get(var) or hasattr(settings, var),
                          f"Critical environment variable {var} not set")
    
    def test_environment_variable_values(self):
        """Test environment variable values for security."""
        # Check for insecure default values
        insecure_defaults = {
            'SECRET_KEY': ['change-me', 'your-secret-key-here', 'secret'],
            'DATABASE_PASSWORD': ['password', 'admin', '123456'],
        }
        
        for var, insecure_values in insecure_defaults.items():
            value = os.environ.get(var, '')
            if value:
                for insecure in insecure_values:
                    self.assertNotEqual(value.lower(), insecure.lower(),
                                      f"Environment variable {var} has insecure value")


class TestFilePermissionsSecurity(TestCase):
    """Test file permissions and access security."""
    
    def test_settings_file_permissions(self):
        """Test that settings files have appropriate permissions."""
        import stat
        from pathlib import Path
        
        # Settings files should not be world-readable in production
        settings_files = [
            'excel_analyzing/web/settings/production.py',
            '.env',
            '.env.production',
        ]
        
        for settings_file in settings_files:
            file_path = Path(settings_file)
            if file_path.exists():
                file_stat = file_path.stat()
                mode = file_stat.st_mode
                
                # Check that file is not world-readable
                world_readable = bool(mode & stat.S_IROTH)
                if os.environ.get('ENVIRONMENT') == 'production':
                    self.assertFalse(world_readable,
                                   f"Settings file {settings_file} should not be world-readable")
    
    def test_static_files_security(self):
        """Test static files security configuration."""
        if hasattr(settings, 'STATIC_ROOT'):
            static_root = settings.STATIC_ROOT
            if static_root:
                static_root_str = str(static_root)
                # Static root should not be in sensitive directories
                sensitive_paths = ['/etc', '/var/log', '/home', '/root']
                for sensitive_path in sensitive_paths:
                    self.assertFalse(static_root_str.startswith(sensitive_path),
                                   f"STATIC_ROOT should not be in sensitive directory: {sensitive_path}")


class TestThirdPartySecurityConfiguration(TestCase):
    """Test third-party package security configuration."""
    
    def test_admin_url_security(self):
        """Test Django admin URL security."""
        from django.urls import reverse
        
        try:
            admin_url = reverse('admin:index')
            # Admin URL should not be the default '/admin/' in production
            if os.environ.get('ENVIRONMENT') == 'production':
                self.assertNotEqual(admin_url, '/admin/',
                                  "Admin URL should be changed from default in production")
        except:
            # If admin is not configured, that's also secure
            pass
    
    def test_cors_security_configuration(self):
        """Test CORS security configuration if django-cors-headers is used."""
        # Check if CORS is configured
        cors_settings = [
            'CORS_ALLOWED_ORIGINS',
            'CORS_ALLOW_ALL_ORIGINS',
            'CORS_ALLOWED_ORIGIN_REGEXES'
        ]
        
        has_cors = any(hasattr(settings, setting) for setting in cors_settings)
        
        if has_cors:
            # If CORS is enabled, it should not allow all origins in production
            if (hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and 
                os.environ.get('ENVIRONMENT') == 'production'):
                self.assertFalse(settings.CORS_ALLOW_ALL_ORIGINS,
                               "CORS should not allow all origins in production")