#!/usr/bin/env python3
"""
Startup script for Git-to-Image UI
This script handles environment setup and launches the Streamlit application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['GITHUB_TOKEN', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the UI.")
        print("Example:")
        print("export GITHUB_TOKEN='your_github_token'")
        print("export GEMINI_API_KEY='your_gemini_api_key'")
        return False
    
    return True

def install_requirements():
    """Install required packages if not already installed"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("📦 Installing frontend requirements...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
            print("✅ Requirements installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    
    return True

def launch_streamlit():
    """Launch the Streamlit application"""
    app_file = Path(__file__).parent / "app.py"
    
    print("🚀 Launching Git-to-Image UI...")
    print("🎮 Nintendo-style interface loading...")
    print("\n" + "="*50)
    print("The UI will open in your default web browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("="*50 + "\n")
    
    try:
        subprocess.run([
            "streamlit", "run", str(app_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Git-to-Image UI...")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it with: pip install streamlit")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🎮 Git-to-Image UI Startup")
    print("=" * 30)
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Launch the application
    if not launch_streamlit():
        sys.exit(1)

if __name__ == "__main__":
    main()
