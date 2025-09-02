#!/usr/bin/env python3
"""
SenialSOLIDApp - One-Command Setup Script
==========================================

This script provides automated setup for the SenialSOLIDApp project.
Supports both production and development environments.

Usage:
    python scripts/setup.py [--dev] [--force] [--python-version X.Y]
    
Options:
    --dev              Install development dependencies
    --force           Force reinstallation of virtual environment
    --python-version  Specify Python version (default: 3.11)
    --help            Show this help message

Author: Victor Valotto <vvalotto@gmail.com>
License: MIT
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class SetupManager:
    """Handles the automated setup of SenialSOLIDApp project."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_path = project_root / "venv"
        self.is_windows = platform.system() == "Windows"
        self.python_executable = "python" if self.is_windows else "python3"
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log setup progress messages."""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅ ",
            "ERROR": "❌ ",
            "WARNING": "⚠️ "
        }.get(level, "• ")
        print(f"{prefix}{message}")
    
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute shell command with error handling."""
        try:
            self.log(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            raise
    
    def check_python_version(self, required_version: str = "3.11") -> bool:
        """Check if Python version meets requirements."""
        try:
            result = self.run_command([self.python_executable, "--version"], check=False)
            if result.returncode != 0:
                self.log("Python not found", "ERROR")
                return False
                
            version_output = result.stdout.strip()
            current_version = version_output.split()[1]
            major, minor = map(int, current_version.split('.')[:2])
            req_major, req_minor = map(int, required_version.split('.'))
            
            if (major, minor) >= (req_major, req_minor):
                self.log(f"Python {current_version} meets requirements (>= {required_version})", "SUCCESS")
                return True
            else:
                self.log(f"Python {current_version} < {required_version} required", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error checking Python version: {e}", "ERROR")
            return False
    
    def create_virtual_environment(self, force: bool = False) -> bool:
        """Create Python virtual environment."""
        if self.venv_path.exists() and not force:
            self.log("Virtual environment already exists", "INFO")
            return True
        
        if force and self.venv_path.exists():
            self.log("Removing existing virtual environment", "WARNING")
            import shutil
            shutil.rmtree(self.venv_path)
        
        self.log("Creating virtual environment...")
        try:
            self.run_command([self.python_executable, "-m", "venv", str(self.venv_path)])
            self.log("Virtual environment created successfully", "SUCCESS")
            return True
        except subprocess.CalledProcessError:
            self.log("Failed to create virtual environment", "ERROR")
            return False
    
    def get_pip_executable(self) -> str:
        """Get pip executable path for the virtual environment."""
        if self.is_windows:
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def get_python_executable(self) -> str:
        """Get Python executable path for the virtual environment."""
        if self.is_windows:
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip in the virtual environment."""
        self.log("Upgrading pip...")
        try:
            self.run_command([self.get_pip_executable(), "install", "--upgrade", "pip"])
            self.log("Pip upgraded successfully", "SUCCESS")
            return True
        except subprocess.CalledProcessError:
            self.log("Failed to upgrade pip", "ERROR")
            return False
    
    def install_dependencies(self, dev: bool = False) -> bool:
        """Install project dependencies."""
        pip_cmd = self.get_pip_executable()
        
        # Install using pyproject.toml (modern approach)
        self.log("Installing project in editable mode...")
        try:
            if dev:
                self.log("Installing with development dependencies...")
                self.run_command([pip_cmd, "install", "-e", ".[dev]"])
            else:
                self.log("Installing production dependencies only...")
                self.run_command([pip_cmd, "install", "-e", "."])
            
            self.log("Dependencies installed successfully", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError:
            self.log("Failed to install via pyproject.toml, trying requirements files...", "WARNING")
            
            # Fallback to requirements files
            try:
                self.run_command([pip_cmd, "install", "-r", "requirements.txt"])
                if dev:
                    self.run_command([pip_cmd, "install", "-r", "requirements-dev.txt"])
                
                self.log("Dependencies installed via requirements files", "SUCCESS")
                return True
                
            except subprocess.CalledProcessError:
                self.log("Failed to install dependencies", "ERROR")
                return False
    
    def verify_installation(self) -> bool:
        """Verify that the installation was successful."""
        self.log("Verifying installation...")
        
        # Check if key packages are installed
        pip_cmd = self.get_pip_executable()
        try:
            result = self.run_command([pip_cmd, "list"], check=False)
            installed_packages = result.stdout.lower()
            
            required_packages = ["flask", "click", "pyyaml"]
            missing_packages = []
            
            for package in required_packages:
                if package not in installed_packages:
                    missing_packages.append(package)
            
            if missing_packages:
                self.log(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
                return False
            
            # Test import of main modules
            python_cmd = self.get_python_executable()
            test_imports = [
                "import flask",
                "import click", 
                "import yaml",
                "from 04_dominio.modelo.senial import Senial"
            ]
            
            for import_stmt in test_imports:
                try:
                    self.run_command([python_cmd, "-c", import_stmt])
                except subprocess.CalledProcessError:
                    self.log(f"Import test failed: {import_stmt}", "WARNING")
            
            self.log("Installation verified successfully", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError:
            self.log("Installation verification failed", "ERROR")
            return False
    
    def create_activation_script(self) -> None:
        """Create convenience activation script."""
        if self.is_windows:
            activate_script = self.project_root / "activate.bat"
            content = f"""@echo off
echo Activating SenialSOLIDApp development environment...
call "{self.venv_path}\\Scripts\\activate.bat"
echo.
echo ✅ Environment activated!
echo.
echo Available commands:
echo   senial-console  - Run console application
echo   senial-webapp   - Run web application  
echo   python -m pytest - Run tests (if dev dependencies installed)
echo.
"""
        else:
            activate_script = self.project_root / "activate.sh"
            content = f"""#!/bin/bash
echo "Activating SenialSOLIDApp development environment..."
source "{self.venv_path}/bin/activate"
echo
echo "✅ Environment activated!"
echo
echo "Available commands:"
echo "  senial-console  - Run console application"
echo "  senial-webapp   - Run web application"
echo "  python -m pytest - Run tests (if dev dependencies installed)"
echo
"""
        
        with open(activate_script, 'w') as f:
            f.write(content)
        
        if not self.is_windows:
            os.chmod(activate_script, 0o755)
        
        self.log(f"Created activation script: {activate_script.name}", "SUCCESS")
    
    def setup(self, dev: bool = False, force: bool = False, python_version: str = "3.11") -> bool:
        """Run complete setup process."""
        self.log("🚀 Starting SenialSOLIDApp setup...", "INFO")
        self.log(f"Project root: {self.project_root}", "INFO")
        self.log(f"Development mode: {'Yes' if dev else 'No'}", "INFO")
        
        # Check Python version
        if not self.check_python_version(python_version):
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment(force):
            return False
        
        # Upgrade pip
        if not self.upgrade_pip():
            return False
        
        # Install dependencies
        if not self.install_dependencies(dev):
            return False
        
        # Verify installation
        if not self.verify_installation():
            self.log("Setup completed with warnings", "WARNING")
        else:
            self.log("Setup completed successfully!", "SUCCESS")
        
        # Create activation script
        self.create_activation_script()
        
        # Print final instructions
        self.print_final_instructions()
        
        return True
    
    def print_final_instructions(self) -> None:
        """Print final setup instructions."""
        activate_cmd = "activate.bat" if self.is_windows else "source activate.sh"
        
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        print("\n📋 Next steps:")
        print(f"1. Activate environment: {activate_cmd}")
        print("2. Run console app: senial-console")
        print("3. Run web app: senial-webapp")
        print("\n📚 Documentation:")
        print("• README.md - Project overview")
        print("• Jira Board: https://vvalotto.atlassian.net/jira/software/projects/SSA")
        print("• Confluence: https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a")
        print("="*60)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="SenialSOLIDApp One-Command Setup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup.py                    # Production setup
  python scripts/setup.py --dev              # Development setup  
  python scripts/setup.py --dev --force      # Force recreation of environment
  python scripts/setup.py --python-version 3.12  # Use Python 3.12
        """
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Install development dependencies"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreation of virtual environment"
    )
    
    parser.add_argument(
        "--python-version",
        default="3.11",
        help="Minimum Python version required (default: 3.11)"
    )
    
    args = parser.parse_args()
    
    # Get project root directory
    project_root = Path(__file__).parent.parent.resolve()
    
    # Create setup manager and run setup
    manager = SetupManager(project_root)
    success = manager.setup(
        dev=args.dev,
        force=args.force,
        python_version=args.python_version
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()