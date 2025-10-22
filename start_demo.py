#!/usr/bin/env python3
"""
Quick launcher for the Multi-Agent Customer Care System Demo
Provides easy access to both Streamlit and FastAPI interfaces.
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed."""
    try:
        import streamlit
        import fastapi
        import openai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_streamlit_demo():
    """Start the Streamlit demo interface."""
    print("🚀 Starting Streamlit Demo Interface...")
    print("📍 URL: http://localhost:8501")
    print("🤖 Features: Interactive chat, agent visualization, memory tracking")
    print()
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🔄 Streamlit demo stopped")

def start_fastapi_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI Server...")
    print("📍 API URL: http://localhost:8000")
    print("📖 Interactive docs: http://localhost:8000/docs")
    print("🔧 Features: REST API, programmatic access")
    print()
    
    try:
        # Start FastAPI
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🔄 FastAPI server stopped")

def start_both():
    """Start both interfaces simultaneously."""
    print("🚀 Starting Both Interfaces...")
    print("💬 Streamlit Demo: http://localhost:8501")
    print("🔧 FastAPI Server: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop all services")
    print()
    
    try:
        # Start both in background
        fastapi_process = subprocess.Popen([sys.executable, "main.py"])
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true"
        ])
        
        # Wait a moment for services to start
        time.sleep(3)
        
        # Open Streamlit in browser
        webbrowser.open("http://localhost:8501")
        
        # Wait for user to stop
        input("Press Enter to stop all services...")
        
    except KeyboardInterrupt:
        pass
    finally:
        print("🔄 Stopping services...")
        try:
            fastapi_process.terminate()
            streamlit_process.terminate()
        except:
            pass
        print("✅ All services stopped")

def show_help():
    """Show help information."""
    print("""
🤖 Multi-Agent Customer Care System Demo Launcher

Usage: python start_demo.py [option]

Options:
  1, streamlit    Start Streamlit demo interface (recommended)
  2, fastapi      Start FastAPI server only
  3, both         Start both interfaces simultaneously
  test            Run system validation tests
  help            Show this help message

Examples:
  python start_demo.py streamlit
  python start_demo.py both

Quick Start:
  1. Ensure virtual environment is activated: source venv/bin/activate
  2. Install dependencies: pip install -r requirements.txt
  3. Configure API keys in .env file (optional)
  4. Run: python start_demo.py streamlit

Demo URLs:
  Streamlit Demo: http://localhost:8501 (beautiful chat interface)
  FastAPI Docs:   http://localhost:8000/docs (API documentation)
  API Endpoint:   http://localhost:8000 (programmatic access)
""")

def run_tests():
    """Run system validation tests."""
    print("🧪 Running system validation tests...")
    try:
        subprocess.run([sys.executable, "test_system.py"])
    except FileNotFoundError:
        print("❌ test_system.py not found")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main launcher function."""
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   Please activate: source venv/bin/activate")
        print()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Parse command line argument
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
    else:
        # Interactive menu
        print("🤖 Multi-Agent Customer Care System Demo")
        print("=" * 50)
        print("1. Streamlit Demo (recommended for demos)")
        print("2. FastAPI Server (for API access)")
        print("3. Both interfaces")
        print("4. Run validation tests")
        print("5. Help")
        print()
        
        choice = input("Select option (1-5): ").strip()
        option_map = {
            "1": "streamlit",
            "2": "fastapi", 
            "3": "both",
            "4": "test",
            "5": "help"
        }
        option = option_map.get(choice, "help")
    
    # Execute based on option
    if option in ["1", "streamlit"]:
        start_streamlit_demo()
    elif option in ["2", "fastapi"]:
        start_fastapi_server()
    elif option in ["3", "both"]:
        start_both()
    elif option == "test":
        run_tests()
    elif option == "help":
        show_help()
    else:
        print(f"❌ Unknown option: {option}")
        show_help()

if __name__ == "__main__":
    main()