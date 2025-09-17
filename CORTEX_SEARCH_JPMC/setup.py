#!/usr/bin/env python3
"""Setup script for JPMC Cortex Search Lab development environment."""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command: str, check: bool = True) -> bool:
    """Run a shell command and return success status."""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False


def check_python_version() -> bool:
    """Check if Python version is 3.9 or higher."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"✗ Python 3.9+ required, found {version.major}.{version.minor}.{version.micro}")
        return False


def create_directories():
    """Create necessary project directories."""
    directories = [
        "logs",
        "data/raw",
        "data/processed", 
        "data/temp",
        "tests/unit",
        "tests/integration",
        "docs/images",
        "sql/setup",
        "sql/queries"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def setup_virtual_environment():
    """Set up Python virtual environment."""
    if not Path("venv").exists():
        print("Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv"):
            return False
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:
        activate_script = "venv/bin/activate"
        pip_command = "venv/bin/pip"
    
    print(f"✓ Virtual environment ready")
    print(f"To activate: source {activate_script}")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    # Determine pip command based on OS
    if platform.system() == "Windows":
        pip_command = "venv\\Scripts\\pip"
    else:
        pip_command = "venv/bin/pip"
    
    print("Installing dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{pip_command} install --upgrade pip"):
        return False
    
    # Install main dependencies
    if not run_command(f"{pip_command} install -r requirements.txt"):
        return False
    
    # Install development dependencies
    if not run_command(f"{pip_command} install -e \".[dev]\""):
        return False
    
    print("✓ Dependencies installed")
    return True


def setup_pre_commit():
    """Set up pre-commit hooks."""
    if platform.system() == "Windows":
        pre_commit_command = "venv\\Scripts\\pre-commit"
    else:
        pre_commit_command = "venv/bin/pre-commit"
    
    print("Setting up pre-commit hooks...")
    if not run_command(f"{pre_commit_command} install"):
        return False
    
    print("✓ Pre-commit hooks installed")
    return True


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not Path(".env").exists():
        if Path("env.template").exists():
            print("Creating .env file from template...")
            with open("env.template", "r") as template:
                content = template.read()
            
            with open(".env", "w") as env_file:
                env_file.write(content)
            
            print("✓ .env file created")
            print("⚠️  Please edit .env file with your Snowflake credentials")
        else:
            print("⚠️  env.template not found, skipping .env creation")
    else:
        print("✓ .env file already exists")


def validate_setup():
    """Validate the setup by running basic checks."""
    print("\nValidating setup...")
    
    # Check if we can import main modules
    try:
        if platform.system() == "Windows":
            python_command = "venv\\Scripts\\python"
        else:
            python_command = "venv/bin/python"
        
        test_command = f"{python_command} -c \"from src.config.settings import app_settings; print('✓ Configuration import successful')\""
        if run_command(test_command, check=False):
            print("✓ Basic imports working")
        else:
            print("⚠️  Basic imports failed - check your .env configuration")
    
    except Exception as e:
        print(f"⚠️  Setup validation error: {e}")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"""
Next steps:

1. Activate your virtual environment:
   {activate_cmd}

2. Edit your .env file with Snowflake credentials:
   # Required fields:
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password

3. Test your Snowflake connection:
   python -c "from src.database.connection import connection_manager; print('✓ Connected' if connection_manager.test_connection() else '✗ Connection failed')"

4. Run the Streamlit application:
   streamlit run src/streamlit_app/main.py

5. Run tests:
   pytest tests/

6. Format and lint code:
   black src/ tests/
   flake8 src/ tests/
   mypy src/

Happy coding! 🚀
""")


def main():
    """Main setup function."""
    print("🏗️  Setting up JPMC Cortex Search Lab development environment...")
    print("="*60)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Creating directories", create_directories),
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up pre-commit hooks", setup_pre_commit),
        ("Creating .env file", create_env_file),
        ("Validating setup", validate_setup),
    ]
    
    for step_name, step_function in steps:
        print(f"\n📋 {step_name}...")
        try:
            if callable(step_function):
                result = step_function()
                if result is False:
                    print(f"✗ {step_name} failed")
                    sys.exit(1)
            else:
                step_function
        except Exception as e:
            print(f"✗ {step_name} failed: {e}")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    main() 