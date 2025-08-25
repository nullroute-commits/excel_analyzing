#!/usr/bin/env python3
"""
Architecture validation tests for the Excel Analyzing containerized platform.

This module validates the architectural components and design choices mentioned
in ARCHITECTURE.md, ensuring that the code aligns with the documented
containerization strategy.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from dotenv import load_dotenv

from excel_analyzing.core.config import Environment, Settings, get_settings


class TestEnvironmentStructure:
    """Test environment file structure validation."""

    def test_env_directory_structure(self):
        """Test that environment configuration directory structure exists."""
        base_path = Path(__file__).parent / "env"
        assert base_path.exists(), "Environment directory 'env/' must exist"

        # Expected service directories
        expected_services = ["web", "database", "cache", "processing"]
        for service in expected_services:
            service_path = base_path / service
            assert service_path.exists(), f"Service directory 'env/{service}/' must exist"

    def test_service_subdirectories(self):
        """Test that each service has proper subdirectories."""
        base_path = Path(__file__).parent / "env"
        
        expected_structure = {
            "web": "django",
            "database": "postgresql", 
            "cache": "redis",
            "processing": "core"
        }
        
        for service, subdir in expected_structure.items():
            subdir_path = base_path / service / subdir
            assert subdir_path.exists(), f"Subdirectory 'env/{service}/{subdir}/' must exist"

    def test_environment_files_exist(self):
        """Test that environment files exist for all environments."""
        base_path = Path(__file__).parent / "env"
        environments = ["development", "test", "production"]
        services = ["web/django", "database/postgresql", "cache/redis", "processing/core"]
        
        for service in services:
            for env in environments:
                env_file = base_path / service / f".env.{env}"
                assert env_file.exists(), f"Environment file 'env/{service}/.env.{env}' must exist"


class TestConfigurationLoading:
    """Test configuration loading per environment."""

    def test_development_environment_loading(self):
        """Test that development environment configuration loads correctly."""
        os.environ["ENVIRONMENT"] = "development"
        settings = get_settings()
        
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.debug is True  # Development should have debug enabled
        assert "dev-web-service" in settings.allowed_hosts or "web-service" in settings.allowed_hosts

    def test_test_environment_loading(self):
        """Test that test environment configuration loads correctly."""
        os.environ["ENVIRONMENT"] = "test"
        settings = get_settings()
        
        assert settings.environment == Environment.TEST
        assert settings.debug is False  # Test should not have debug enabled
        assert "test-web-service" in settings.allowed_hosts

    def test_production_environment_loading(self):
        """Test that production environment configuration loads correctly."""
        os.environ["ENVIRONMENT"] = "production"
        settings = get_settings()
        
        assert settings.environment == Environment.PRODUCTION
        assert settings.debug is False  # Production should never have debug enabled

    def test_dynamic_configuration_loading(self):
        """Test that configuration loading is dynamic based on ENVIRONMENT variable."""
        # Test that changing environment variable affects configuration
        original_env = os.environ.get("ENVIRONMENT")
        
        try:
            # Test development
            os.environ["ENVIRONMENT"] = "development"
            dev_settings = get_settings()
            assert dev_settings.environment == Environment.DEVELOPMENT
            
            # Test test
            os.environ["ENVIRONMENT"] = "test"
            test_settings = get_settings()
            assert test_settings.environment == Environment.TEST
            
            # Verify they're different
            assert dev_settings.environment != test_settings.environment
            
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["ENVIRONMENT"] = original_env
            else:
                os.environ.pop("ENVIRONMENT", None)


class TestHostnameBasedServiceDiscovery:
    """Test hostname-based service discovery."""

    def test_hostname_based_database_configuration(self):
        """Test that database configuration uses hostnames not localhost."""
        settings = get_settings()
        
        # Database host should not be localhost or 127.0.0.1
        assert settings.database_host not in ["localhost", "127.0.0.1"]
        assert "service" in settings.database_host.lower()  # Should contain 'service'
        
        # Database URL should use hostname
        assert "localhost" not in settings.database_url
        assert "127.0.0.1" not in settings.database_url

    def test_hostname_based_redis_configuration(self):
        """Test that Redis configuration uses hostnames not localhost."""
        settings = get_settings()
        
        # Redis host should not be localhost or 127.0.0.1
        assert settings.redis_host not in ["localhost", "127.0.0.1"]
        assert "service" in settings.redis_host.lower()  # Should contain 'service'
        
        # Redis URL should use hostname
        assert "localhost" not in settings.redis_url
        assert "127.0.0.1" not in settings.redis_url

    def test_environment_specific_hostnames(self):
        """Test that different environments use environment-specific hostnames."""
        test_cases = [
            ("development", ["dev-", "web-service"]),
            ("test", ["test-", "web-service"]),
            ("production", ["prod-", "web-service"])
        ]
        
        original_env = os.environ.get("ENVIRONMENT")
        
        try:
            for env_name, expected_patterns in test_cases:
                os.environ["ENVIRONMENT"] = env_name
                settings = get_settings()
                
                # Check if any expected pattern is in allowed hosts
                has_expected_pattern = any(
                    any(pattern in host for host in settings.allowed_hosts)
                    for pattern in expected_patterns
                )
                assert has_expected_pattern, f"Environment {env_name} should have hostname patterns {expected_patterns}"
                
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["ENVIRONMENT"] = original_env
            else:
                os.environ.pop("ENVIRONMENT", None)


class TestAlpineContainerUsage:
    """Test Alpine container usage validation."""

    def test_dockerfile_uses_alpine(self):
        """Test that Dockerfiles use Alpine base images."""
        dockerfile_paths = [
            Path(__file__).parent / "Dockerfile",
            Path(__file__).parent / "Dockerfile.dev",
            Path(__file__).parent / "Dockerfile.test",
        ]
        
        for dockerfile_path in dockerfile_paths:
            if dockerfile_path.exists():
                content = dockerfile_path.read_text()
                
                # Should contain alpine in base image
                alpine_found = any(
                    "alpine" in line.lower() and "from" in line.lower()
                    for line in content.split('\n')
                )
                assert alpine_found, f"Dockerfile {dockerfile_path.name} should use Alpine base image"

    def test_production_dockerfile_multistage(self):
        """Test that production Dockerfile implements multistage builds."""
        dockerfile_path = Path(__file__).parent / "Dockerfile"
        
        if dockerfile_path.exists():
            content = dockerfile_path.read_text()
            
            # Should have multiple FROM statements (multistage)
            from_statements = [
                line for line in content.split('\n')
                if line.strip().lower().startswith('from')
            ]
            assert len(from_statements) >= 2, "Production Dockerfile should use multistage builds (multiple FROM statements)"
            
            # Should have AS aliases for stages
            as_aliases = [
                line for line in from_statements
                if " as " in line.lower()
            ]
            assert len(as_aliases) >= 1, "Production Dockerfile should name build stages with AS aliases"


class TestDockerComposeConfiguration:
    """Test Docker Compose configuration validation."""

    def test_docker_compose_files_exist(self):
        """Test that Docker Compose files exist for different environments."""
        compose_files = [
            "docker-compose.yml",          # Production
            "docker-compose.dev.yml",      # Development
            "docker-compose.test.yml",     # Test
        ]
        
        for compose_file in compose_files:
            compose_path = Path(__file__).parent / compose_file
            assert compose_path.exists(), f"Docker Compose file {compose_file} must exist"

    def test_docker_compose_service_naming(self):
        """Test that Docker Compose uses proper service naming conventions."""
        compose_path = Path(__file__).parent / "docker-compose.yml"
        
        if compose_path.exists():
            content = compose_path.read_text()
            
            # Should contain service names that follow hostname pattern
            expected_services = ["web-service", "db-service", "cache-service"]
            for service in expected_services:
                assert service in content or service.replace("-", "_") in content, \
                    f"Docker Compose should define {service} service"


class TestSecurityConfiguration:
    """Test security configuration validation."""

    def test_django_secret_key_security(self):
        """Test that Django secret key meets security requirements."""
        settings = get_settings()
        
        # Skip test if using environment variable placeholder (production)
        if settings.django_secret_key.startswith("${") or not settings.django_secret_key:
        # Skip test if in production and secret key is not set (i.e., expected to be provided via env var)
        if settings.environment == Environment.PRODUCTION and not settings.django_secret_key:
            pytest.skip("Production: secret key expected to be set via environment variable")
            
        # Secret key should be long enough for security
        assert len(settings.django_secret_key) >= 50, "Django secret key should be at least 50 characters"
        
        # Should not be default insecure key in production (except placeholder values)
        if settings.environment == Environment.PRODUCTION:
            insecure_patterns = ["dev-secret", "test-secret", "django-insecure"]
            assert not any(pattern in settings.django_secret_key.lower() 
                         for pattern in insecure_patterns), \
                "Production should not use development/test secret keys"

    def test_allowed_hosts_configuration(self):
        """Test that allowed hosts are properly configured."""
        settings = get_settings()
        
        # Should not allow all hosts in production
        if settings.environment == Environment.PRODUCTION:
            dangerous_hosts = ["*", "0.0.0.0"]
            assert not any(host in settings.allowed_hosts for host in dangerous_hosts), \
                "Production should not allow wildcard hosts"
        
        # Should include service hostnames
        assert any("service" in host for host in settings.allowed_hosts), \
            "Allowed hosts should include service hostnames"


def run_architecture_tests():
    """Run all architecture validation tests."""
    print("🏗️  Running architecture validation tests...")
    
    # Run pytest on this file
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All architecture tests passed!")
    else:
        print("❌ Some architecture tests failed!")
        
    return result.returncode == 0


if __name__ == "__main__":
    success = run_architecture_tests()
# (Removed custom test runner and main block; rely on pytest's native test discovery)