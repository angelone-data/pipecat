#!/usr/bin/env python3
"""
Script to download Whisper model with comprehensive SSL bypass.
"""

import os
import ssl
import urllib3
import requests
from pathlib import Path

# Comprehensive SSL bypass
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Set environment variables
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

def download_whisper_tiny():
    """Download the tiny Whisper model with SSL bypass."""
    print("🔄 Downloading Whisper tiny model with SSL bypass...")
    
    try:
        # Import after setting SSL bypass
        import huggingface_hub
        from huggingface_hub import snapshot_download
        
        # Configure huggingface_hub session
        session = huggingface_hub.utils._http.get_session()
        session.verify = False
        
        # Create cache directory
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Cache directory: {cache_dir}")
        
        # Try to download the model
        model_path = snapshot_download(
            repo_id="openai/whisper-tiny",
            cache_dir=str(cache_dir),
            local_files_only=False,
            token=None
        )
        
        print(f"✅ Model downloaded to: {model_path}")
        return model_path
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("🔄 Trying alternative approach...")
        
        # Try with a different model
        try:
            model_path = snapshot_download(
                repo_id="openai/whisper-base",
                cache_dir=str(cache_dir),
                local_files_only=False,
                token=None
            )
            print(f"✅ Alternative model downloaded to: {model_path}")
            return model_path
        except Exception as e2:
            print(f"❌ Alternative download also failed: {e2}")
            return None

if __name__ == "__main__":
    model_path = download_whisper_tiny()
    if model_path:
        print(f"\n📁 Use this path in your bot.py:")
        print(f'model_path="{model_path}"')
    else:
        print("\n❌ Failed to download model. You may need to check your internet connection or SSL settings.")
