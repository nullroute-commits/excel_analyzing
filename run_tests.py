#!/usr/bin/env python3
"""
Comprehensive test runner script for excel_analyzing project.

This script provides a convenient interface for running different types of tests
with appropriate configurations and reporting.
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any
import json


def run_command(command: str, description: str = "", timeout: int = 300) -> Dict[str, Any]:
    """Run a command and capture results."""
    print(f"\n{'='*60}")
    print(f"Running: {description or command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS ({duration:.2f}s)")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ FAILED ({duration:.2f}s)")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
        
        return {
            'command': command,
            'description': description,
            'returncode': result.returncode,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT after {timeout}s")
        return {
            'command': command,
            'description': description,
            'returncode': -1,
            'duration': timeout,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return {
            'command': command,
            'description': description,
            'returncode': -2,
            'duration': time.time() - start_time,
            'stdout': '',
            'stderr': str(e)
        }


def run_unit_tests(args) -> List[Dict[str, Any]]:
    """Run unit tests."""
    results = []
    
    # Basic unit tests
    cmd = "pytest tests/unit/ -v --tb=short"
    if args.coverage:
        cmd += " --cov=excel_analyzing --cov-report=html --cov-report=term"
    
    results.append(run_command(cmd, "Unit Tests"))
    
    return results


def run_integration_tests(args) -> List[Dict[str, Any]]:
    """Run integration tests."""
    results = []
    
    # Set up test database if needed
    if args.database:
        db_setup = "python manage.py migrate --settings=excel_analyzing.web.settings.test"
        results.append(run_command(db_setup, "Database Setup"))
    
    # Integration tests
    cmd = "pytest tests/integration/ -v --tb=short"
    if args.parallel:
        cmd += " -n auto"
    
    results.append(run_command(cmd, "Integration Tests", timeout=600))
    
    return results


def run_security_tests(args) -> List[Dict[str, Any]]:
    """Run security tests."""
    results = []
    
    # Security test suite
    results.append(run_command(
        "pytest tests/security/ -v --tb=short",
        "Security Test Suite"
    ))
    
    # Static security analysis
    results.append(run_command(
        "bandit -r excel_analyzing/ -f json -o bandit-report.json || echo 'Bandit completed with findings'",
        "Bandit Security Scan"
    ))
    
    # Dependency security check
    results.append(run_command(
        "safety check --json || echo 'Safety completed'",
        "Safety Dependency Check"
    ))
    
    return results


def run_performance_tests(args) -> List[Dict[str, Any]]:
    """Run performance tests."""
    results = []
    
    cmd = "pytest tests/performance/ -v --tb=short --benchmark-json=benchmark.json"
    if args.benchmark:
        cmd += " --benchmark-compare"
    
    results.append(run_command(cmd, "Performance Tests", timeout=900))
    
    return results


def run_regression_tests(args) -> List[Dict[str, Any]]:
    """Run regression tests."""
    results = []
    
    cmd = "pytest tests/regression/ -v --tb=short"
    
    results.append(run_command(cmd, "Regression Tests"))
    
    return results


def run_e2e_tests(args) -> List[Dict[str, Any]]:
    """Run end-to-end tests."""
    results = []
    
    # Install browser dependencies
    results.append(run_command(
        "playwright install chromium",
        "Install Playwright Browser"
    ))
    
    # E2E tests
    cmd = "pytest tests/e2e/ -v --tb=short"
    if args.headed:
        cmd += " --headed"
    if args.video:
        cmd += " --video=on"
    
    results.append(run_command(cmd, "End-to-End Tests", timeout=1200))
    
    return results


def run_linting(args) -> List[Dict[str, Any]]:
    """Run code linting and formatting checks."""
    results = []
    
    # Black formatting check
    results.append(run_command(
        "black --check excel_analyzing/",
        "Black Formatting Check"
    ))
    
    # Flake8 linting
    results.append(run_command(
        "flake8 excel_analyzing/",
        "Flake8 Linting"
    ))
    
    # Import sorting check
    results.append(run_command(
        "isort --check-only excel_analyzing/",
        "Import Sorting Check"
    ))
    
    # Type checking
    results.append(run_command(
        "mypy excel_analyzing/ --ignore-missing-imports",
        "Type Checking"
    ))
    
    return results


def generate_report(all_results: List[Dict[str, Any]], output_file: str = None):
    """Generate a comprehensive test report."""
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r['returncode'] == 0)
    failed_tests = total_tests - passed_tests
    total_duration = sum(r['duration'] for r in all_results)
    
    report = {
        'summary': {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration
        },
        'results': all_results
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Total Duration: {total_duration:.2f}s")
    
    # Print failed tests
    if failed_tests > 0:
        print(f"\n{'='*60}")
        print("FAILED TESTS")
        print(f"{'='*60}")
        for result in all_results:
            if result['returncode'] != 0:
                print(f"❌ {result['description']}: {result['stderr'][:100]}...")
    
    # Save detailed report
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {output_file}")
    
    return report


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner for excel_analyzing")
    
    # Test categories
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--security', action='store_true', help='Run security tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--regression', action='store_true', help='Run regression tests')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests')
    parser.add_argument('--lint', action='store_true', help='Run linting and formatting checks')
    parser.add_argument('--all', action='store_true', help='Run all test categories')
    
    # Options
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--database', action='store_true', help='Set up test database')
    parser.add_argument('--benchmark', action='store_true', help='Compare performance benchmarks')
    parser.add_argument('--headed', action='store_true', help='Run E2E tests in headed mode')
    parser.add_argument('--video', action='store_true', help='Record videos for E2E tests')
    parser.add_argument('--output', type=str, help='Output file for test report')
    
    args = parser.parse_args()
    
    # If no specific test category is specified, run basic tests
    if not any([args.unit, args.integration, args.security, args.performance, 
                args.regression, args.e2e, args.lint, args.all]):
        args.unit = True
        args.lint = True
    
    all_results = []
    
    print("🚀 Starting comprehensive test suite...")
    print(f"Working directory: {os.getcwd()}")
    
    # Run requested test categories
    if args.all or args.lint:
        all_results.extend(run_linting(args))
    
    if args.all or args.unit:
        all_results.extend(run_unit_tests(args))
    
    if args.all or args.integration:
        all_results.extend(run_integration_tests(args))
    
    if args.all or args.security:
        all_results.extend(run_security_tests(args))
    
    if args.all or args.performance:
        all_results.extend(run_performance_tests(args))
    
    if args.all or args.regression:
        all_results.extend(run_regression_tests(args))
    
    if args.all or args.e2e:
        all_results.extend(run_e2e_tests(args))
    
    # Generate report
    report = generate_report(all_results, args.output)
    
    # Exit with appropriate code
    if report['summary']['failed'] > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()