#!/usr/bin/env python3
"""
FlavorLab Test Runner

This script runs the complete test suite for the FlavorLab backend MVP.
It provides options for running different test categories and generates
comprehensive test reports.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False, e.stdout, e.stderr


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import pytest
        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest is not installed. Installing...")
        success, _, _ = run_command("pip install pytest pytest-cov", "Installing pytest")
        if not success:
            return False
    
    try:
        import fastapi
        print("✅ FastAPI is installed")
    except ImportError:
        print("❌ FastAPI is not installed. Installing...")
        success, _, _ = run_command("pip install fastapi", "Installing FastAPI")
        if not success:
            return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy is installed")
    except ImportError:
        print("❌ SQLAlchemy is not installed. Installing...")
        success, _, _ = run_command("pip install sqlalchemy", "Installing SQLAlchemy")
        if not success:
            return False
    
    return True


def run_tests(test_path=None, verbose=False, coverage=False, parallel=False):
    """Run the test suite."""
    print("🧪 Running FlavorLab Test Suite")
    print("=" * 50)
    
    # Build pytest command
    cmd_parts = ["python", "-m", "pytest"]
    
    if verbose:
        cmd_parts.append("-v")
    
    if coverage:
        cmd_parts.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    if parallel:
        cmd_parts.extend(["-n", "auto"])
    
    if test_path:
        cmd_parts.append(test_path)
    else:
        cmd_parts.append("tests/")
    
    cmd = " ".join(cmd_parts)
    
    print(f"Command: {cmd}")
    print("-" * 50)
    
    success, stdout, stderr = run_command(cmd, "Running tests")
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
        
        if coverage:
            print("\n📊 Coverage report generated:")
            print("   - HTML report: htmlcov/index.html")
            print("   - Terminal report: See output above")
        
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        print("\nDetailed output:")
        print(stdout)
        if stderr:
            print("\nErrors:")
            print(stderr)
        
        return False


def run_specific_test_category(category):
    """Run tests for a specific category."""
    test_categories = {
        "models": "tests/test_models/",
        "api": "tests/test_api/",
        "services": "tests/test_services/",
        "scripts": "tests/test_scripts/",
        "auth": "tests/test_api/test_auth.py",
        "users": "tests/test_api/test_users.py",
        "entities": "tests/test_api/test_entities.py",
        "search": "tests/test_services/test_search_service.py"
    }
    
    if category not in test_categories:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_categories.keys())}")
        return False
    
    test_path = test_categories[category]
    print(f"🎯 Running {category} tests...")
    
    return run_tests(test_path=test_path, verbose=True)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="FlavorLab Test Runner")
    parser.add_argument("--category", "-c", help="Run specific test category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    parser.add_argument("--path", help="Run tests from specific path")
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed!")
        sys.exit(1)
    
    if args.check_deps:
        print("✅ All dependencies are available!")
        return
    
    # Run tests
    if args.category:
        success = run_specific_test_category(args.category)
    else:
        success = run_tests(
            test_path=args.path,
            verbose=args.verbose,
            coverage=args.coverage,
            parallel=args.parallel
        )
    
    if success:
        print("\n🚀 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test suite failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
