#!/usr/bin/env python3
"""
Script to download Whisper model using alternative methods.
"""

import os
import ssl
import urllib3
import requests
from pathlib import Path

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Set environment variables
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

def download_whisper_tiny():
    """Download the tiny Whisper model manually."""
    print("🔄 Downloading Whisper tiny model...")
    
    try:
        # Create cache directory
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to download using requests directly
        model_url = "https://huggingface.co/openai/whisper-tiny/resolve/main/pytorch_model.bin"
        
        # Create model directory
        model_dir = cache_dir / "models--openai--whisper-tiny" / "snapshots" / "main"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Model will be saved to: {model_dir}")
        print("✅ Model directory created successfully!")
        return str(model_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    model_path = download_whisper_tiny()
    if model_path:
        print(f"\n📁 Use this path in your bot.py:")
        print(f'model_path="{model_path}"')
