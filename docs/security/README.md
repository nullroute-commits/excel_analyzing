# Security Test Suite

## 🛡️ Overview

This comprehensive security test suite provides automated security testing for the Excel Analyzing application, including vulnerability scanning, static analysis, secret detection, and security configuration validation.

## 🚀 Quick Start

### Run All Security Tests
```bash
# Run the complete security test suite
python run_security_tests.py

# Or run specific test categories
pytest tests/security/ -v
```

### Run Individual Security Tools
```bash
# Static security analysis
bandit -r excel_analyzing/

# Dependency vulnerability scanning  
safety check

# Pattern-based security analysis
semgrep --config=auto excel_analyzing/
```

## 📁 Security Test Structure

```
tests/security/
├── test_security_suite.py         # Core security tests (26 tests)
├── test_api_security.py           # API security tests (13 tests)  
├── test_configuration_security.py # Configuration tests (18 tests)
└── __init__.py

.github/workflows/
└── security-testing.yml           # Automated security pipeline

docs/security/
└── security-testing-strategy.md   # Comprehensive documentation

Security Configuration:
├── .bandit                         # Bandit security linting config
├── .secrets.baseline              # Secret detection baseline
└── run_security_tests.py         # Security test runner script
```

## 🧪 Test Categories

### 1. Core Security Tests (`test_security_suite.py`)
- **Input Validation**: File upload security, path traversal prevention, filename sanitization
- **Authentication**: Password strength, session security, brute force protection
- **Data Security**: Encryption validation, sensitive data detection, access controls
- **Dependency Security**: Vulnerability scanning, integrity checks, outdated packages
- **Configuration Security**: Debug mode, secret keys, security headers

### 2. API Security Tests (`test_api_security.py`)
- **Authentication**: Token validation, unauthorized access prevention
- **Authorization**: User data isolation, admin access controls
- **Input Validation**: Malicious JSON, SQL injection, file upload security
- **Rate Limiting**: API abuse prevention
- **Error Handling**: Information disclosure prevention
- **Security Headers**: CORS, XSS, clickjacking protection

### 3. Configuration Security Tests (`test_configuration_security.py`)
- **Production Security**: Debug mode, HTTPS enforcement, security headers
- **Database Security**: SSL configuration, credential validation
- **Session Security**: Cookie settings, CSRF protection
- **Environment Variables**: Secret validation, insecure defaults detection
- **File Permissions**: Settings file security, static file configuration
- **Third-party Security**: Admin URL, CORS configuration

## 🔄 CI/CD Integration

### GitHub Actions Security Workflow

The security pipeline runs automatically on:
- **Push** to main/develop branches
- **Pull Requests** to main/develop  
- **Daily Schedule** (2 AM UTC)
- **Manual Trigger** with scan type selection

#### Workflow Jobs:
1. **Dependency Scanning**: Safety, pip-audit, outdated package detection
2. **Static Analysis**: Bandit SAST, Semgrep pattern analysis
3. **Secret Scanning**: TruffleHog, detect-secrets
4. **Security Tests**: Complete test suite execution
5. **Container Security**: Trivy, Hadolint scanning
6. **Security Reporting**: Automated summary and artifacts

### Manual Workflow Triggers
```bash
# Run specific security scans
gh workflow run security-testing.yml -f scan_type=dependency
gh workflow run security-testing.yml -f scan_type=sast
gh workflow run security-testing.yml -f scan_type=secrets
gh workflow run security-testing.yml -f scan_type=container
gh workflow run security-testing.yml -f scan_type=all
```

## 🔧 Security Tools Configuration

### Bandit (Python Security Linting)
- **Config**: `.bandit`
- **Exclusions**: Test directories, migrations, virtual environments
- **Severity**: High and Medium confidence issues
- **Format**: JSON output for CI/CD integration

### detect-secrets (Secret Detection)
- **Baseline**: `.secrets.baseline`
- **Plugins**: AWS, GitHub, JWT, private keys, high entropy strings
- **Filters**: Common false positives, templated secrets, UUIDs

### Safety (Dependency Vulnerability Scanning)
- **Database**: Python package vulnerability database
- **Integration**: Automated in CI/CD with graceful error handling
- **Reporting**: JSON format for parsing and analysis

## 📊 Security Metrics

### Test Coverage
- **Total Tests**: 57 security tests
- **Coverage**: 25% (focused on security-critical paths)
- **Categories**: 6 comprehensive security test categories

### Security Scanning
- **SAST Tools**: Bandit, Semgrep
- **Dependency Scanning**: Safety, pip-audit
- **Secret Detection**: TruffleHog, detect-secrets
- **Container Security**: Trivy, Hadolint

## 🚨 Security Issues & Response

### Issue Severity Levels
- **Critical**: Active security breach (immediate response)
- **High**: Significant vulnerability (same-day response)
- **Medium**: Security issue (weekly response)
- **Low**: Security improvement (monthly response)

### Quality Gates
- **Zero Critical/High Issues**: Block deployment
- **Dependency Security**: All packages pass security scans
- **Secret Detection**: No hardcoded secrets in code
- **Configuration Security**: Production settings validated

## 🛠️ Development Workflow

### Pre-commit Security Checks
```bash
# Install pre-commit hooks
pre-commit install

# Run security checks before commit
pre-commit run --all-files
```

### Local Security Testing
```bash
# Quick security test
pytest tests/security/test_security_suite.py -v

# Full security analysis
python run_security_tests.py

# Security-focused coverage
pytest tests/security/ --cov=excel_analyzing --cov-report=html
```

### Adding New Security Tests
1. **Choose Category**: Core, API, or Configuration security
2. **Follow Patterns**: Use existing test structure and naming
3. **Add Markers**: Use appropriate pytest markers
4. **Update Documentation**: Add test description and rationale
5. **Test Thoroughly**: Verify both positive and negative cases

## 📚 Documentation

- **[Security Testing Strategy](docs/security/security-testing-strategy.md)**: Comprehensive security documentation
- **[Technical Design](TECHNICAL_DESIGN.md)**: Security architecture overview
- **[Testing README](TESTING_README.md)**: General testing information

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Review security scan results
- **Monthly**: Update security dependencies
- **Quarterly**: Review and update security tests
- **Annually**: Complete security architecture review

### Tool Updates
- **Dependency Scanning**: Keep Safety database updated
- **SAST Tools**: Update Bandit and Semgrep rules
- **Secret Detection**: Maintain secret pattern baselines
- **Documentation**: Update security procedures and guidelines

## 🎯 Security Best Practices

1. **Defense in Depth**: Multiple security layers and controls
2. **Least Privilege**: Minimal access rights and permissions
3. **Fail Secure**: Secure defaults and error handling
4. **Input Validation**: Comprehensive input sanitization
5. **Security Monitoring**: Continuous security monitoring and alerting

---

For detailed security information, see [Security Testing Strategy](docs/security/security-testing-strategy.md).

**Security Team Contact**: For security issues, create an issue or contact the security team.