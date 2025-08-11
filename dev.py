#!/usr/bin/env python3
"""
Development helper script for Bouncer
Usage: python dev.py <command>

Commands:
  install-dev    Install package in development mode with dev dependencies
  test           Run tests
  test-cov       Run tests with coverage
  lint           Run linting (flake8)
  format         Format code (black)
  type-check     Run type checking (mypy)
  build          Build the package
  clean          Clean build artifacts
  all-checks     Run all quality checks (test, lint, format, type-check)
"""

import subprocess
import sys
import shutil
from pathlib import Path

def run_cmd(cmd, **kwargs):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, shell=True, **kwargs)

def install_dev():
    """Install package in development mode"""
    run_cmd([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])

def test():
    """Run tests"""
    run_cmd([sys.executable, "-m", "pytest"])

def test_cov():
    """Run tests with coverage"""
    run_cmd([sys.executable, "-m", "pytest", "--cov=bouncer", "--cov-report=html", "--cov-report=term"])

def lint():
    """Run linting"""
    run_cmd([sys.executable, "-m", "flake8", "bouncer", "tests"])

def format_code():
    """Format code"""
    run_cmd([sys.executable, "-m", "black", "bouncer", "tests"])

def type_check():
    """Run type checking"""
    run_cmd([sys.executable, "-m", "mypy", "bouncer"])

def build():
    """Build the package"""
    run_cmd([sys.executable, "-m", "build"])

def clean():
    """Clean build artifacts"""
    dirs_to_remove = [
        "build", "dist", "*.egg-info", 
        "__pycache__", ".pytest_cache", 
        ".coverage", "htmlcov", ".mypy_cache"
    ]
    
    for pattern in dirs_to_remove:
        for path in Path(".").glob(f"**/{pattern}"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed file: {path}")

def all_checks():
    """Run all quality checks"""
    print("=== Running all quality checks ===")
    
    print("\n1. Formatting code...")
    format_code()
    
    print("\n2. Running linting...")
    if lint().returncode != 0:
        print("❌ Linting failed!")
        return 1
    
    print("\n3. Running type checking...")
    if type_check().returncode != 0:
        print("❌ Type checking failed!")
        return 1
    
    print("\n4. Running tests...")
    if test().returncode != 0:
        print("❌ Tests failed!")
        return 1
    
    print("\n✅ All checks passed!")
    return 0

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    command = sys.argv[1]
    
    commands = {
        "install-dev": install_dev,
        "test": test,
        "test-cov": test_cov,
        "lint": lint,
        "format": format_code,
        "type-check": type_check,
        "build": build,
        "clean": clean,
        "all-checks": all_checks,
    }
    
    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1
    
    return commands[command]()

if __name__ == "__main__":
    sys.exit(main() or 0)
