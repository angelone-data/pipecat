#!/usr/bin/env python3
"""
Script to download Whisper model locally to avoid SSL issues.
"""

import os
import ssl
import urllib3
import requests
from huggingface_hub import snapshot_download
from faster_whisper import WhisperModel

# Disable SSL verification to avoid certificate issues
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure requests to not verify SSL
requests.packages.urllib3.disable_warnings()
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

def download_whisper_model():
    """Download the Whisper model locally."""
    print("🔄 Downloading Whisper model locally...")
    
    try:
        # Create a local cache directory
        cache_dir = os.path.expanduser("~/.cache/pipecat/whisper")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Try downloading with SSL verification disabled
        import huggingface_hub
        huggingface_hub.utils._http.get_session().verify = False
        
        # Download the model
        model_path = snapshot_download(
            repo_id="Systran/faster-distil-whisper-medium.en",
            cache_dir=cache_dir,
            local_files_only=False,
            token=None
        )
        
        print(f"✅ Model downloaded to: {model_path}")
        return model_path
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("🔄 Trying alternative approach...")
        
        # Try with a different model or approach
        try:
            # Try downloading the base model instead
            model_path = snapshot_download(
                repo_id="Systran/faster-whisper-base.en",
                cache_dir=cache_dir,
                local_files_only=False,
                token=None
            )
            print(f"✅ Alternative model downloaded to: {model_path}")
            return model_path
        except Exception as e2:
            print(f"❌ Alternative download also failed: {e2}")
            return None

if __name__ == "__main__":
    model_path = download_whisper_model()
    if model_path:
        print(f"\n📁 Use this path in your bot.py:")
        print(f"model_path=\"{model_path}\"")
