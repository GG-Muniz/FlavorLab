#!/usr/bin/env python3
"""
FlavorLab Backend Setup Script

This script helps set up the FlavorLab backend environment and database.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python():
    """Check if Python is available."""
    print("🐍 Checking Python installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python found: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python not found: {e}")
        return False


def install_dependencies():
    """Install Python dependencies."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    )


def setup_environment():
    """Set up environment file."""
    env_example = Path(__file__).parent / ".env.example"
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        print("📝 Creating .env file from template...")
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  .env.example not found, skipping environment setup")
        return True


def initialize_database():
    """Initialize the database."""
    init_script = Path(__file__).parent / "scripts" / "init_db.py"
    if not init_script.exists():
        print("❌ Database initialization script not found")
        return False
    
    return run_command(
        f"{sys.executable} {init_script}",
        "Initializing database"
    )


def main():
    """Main setup function."""
    print("🚀 FlavorLab Backend Setup")
    print("=" * 40)
    
    steps = [
        ("Check Python", check_python),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Initialize Database", initialize_database)
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"⚠️  {step_name} failed, but continuing...")
    
    print("\n" + "=" * 40)
    print(f"Setup completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("🎉 FlavorLab backend setup completed successfully!")
        print("\nNext steps:")
        print("1. Review and update .env file if needed")
        print("2. Run: uvicorn app.main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("⚠️  Setup completed with some issues. Please review the output above.")
    
    return success_count == total_steps


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
