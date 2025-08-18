#!/usr/bin/env python3
"""
Run FastAPI development server with auto-reload
"""

import subprocess
import sys

def main():
    print("🔥 FastAPI Development Server with Auto-Reload")
    print("=" * 40)
    print("Server will restart automatically when you save changes")
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    # Run uvicorn with reload for development
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--reload"
    ])

if __name__ == "__main__":
    main()
