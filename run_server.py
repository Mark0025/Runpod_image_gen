#!/usr/bin/env python3
"""
Run FastAPI server with uvicorn
"""

import subprocess
import sys

def main():
    print("🚀 Starting FastAPI server with uvicorn")
    print("=" * 40)
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    # Run uvicorn directly
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001"
    ])

if __name__ == "__main__":
    main()
