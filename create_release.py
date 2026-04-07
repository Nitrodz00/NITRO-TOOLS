#!/usr/bin/env python3
"""
GitHub Release Creator for NITROTOOLS v3.1.0
Creates a GitHub release with the executable file.
"""

import requests
import json
import os

# GitHub repository info
REPO_OWNER = "Nitrodz00"
REPO_NAME = "NITRO-TOOLS"
TAG_NAME = "v3.1.0"

# Release information
RELEASE_TITLE = "NITROTOOLS v3.1.0 - Professional Grade Release"
RELEASE_NOTES = """🎉 NITROTOOLS v3.1.0 - Professional Grade Release

🎛️ NEW: Expert Mode with 5 optimization categories
🛡️ NEW: Compatibility Manager for automatic feature detection  
🚀 NEW: Full AMD GPU support with vendor-specific optimizations
📊 Enhanced: Performance monitoring with GPU memory tracking
⚡ Improved: Responsive UI with QTimer implementation
📦 NEW: Intelligent caching system (40% memory reduction)

🔧 Critical Fixes:
• Shadow control now works properly in-game
• Shortcut creation error resolved
• Enhanced error handling for better stability

📦 Installation:
1. Download NITROTOOLS_PUBG_MOBILE_v3.1.0.exe
2. Run as Administrator
3. Enjoy professional-grade optimizations!

📋 System Requirements:
• Windows 10/11 (Build 10240+)
• 4GB RAM minimum (6GB+ recommended)
• Administrator privileges required
• GameLoop 7.1 or later

🚀 Ready for professional gaming experience!"""

def create_github_release():
    """Create GitHub release with assets."""
    
    # You need to provide a GitHub token
    # Create one at: https://github.com/settings/tokens
    # Required scopes: repo
    
    token = input("Enter your GitHub token (or press Enter to skip): ").strip()
    
    if not token:
        print("❌ No token provided. Skipping automatic release creation.")
        print("Please create the release manually at:")
        print("https://github.com/Nitrodz00/NITRO-TOOLS/releases/new")
        return False
    
    # API URLs
    releases_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    
    # Headers
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # Release data
    release_data = {
        "tag_name": TAG_NAME,
        "name": RELEASE_TITLE,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": False
    }
    
    try:
        print("🚀 Creating GitHub release...")
        response = requests.post(releases_url, headers=headers, json=release_data)
        
        if response.status_code == 201:
            release_info = response.json()
            release_id = release_info["id"]
            upload_url = release_info["upload_url"].replace("{?name,label}", "")
            
            print(f"✅ Release created successfully! ID: {release_id}")
            
            # Upload executable file
            exe_path = "dist/NITROTOOLS_PUBG_MOBILE_v3.1.0.exe"
            if os.path.exists(exe_path):
                print(f"📤 Uploading {exe_path}...")
                
                with open(exe_path, "rb") as f:
                    file_content = f.read()
                
                upload_headers = {
                    "Authorization": f"token {token}",
                    "Content-Type": "application/octet-stream"
                }
                
                upload_params = {
                    "name": "NITROTOOLS_PUBG_MOBILE_v3.1.0.exe"
                }
                
                upload_response = requests.post(
                    upload_url,
                    headers=upload_headers,
                    params=upload_params,
                    data=file_content
                )
                
                if upload_response.status_code == 201:
                    print("✅ Executable uploaded successfully!")
                else:
                    print(f"❌ Failed to upload executable: {upload_response.status_code}")
                    print(upload_response.text)
            
            print(f"🎉 Release available at: {release_info['html_url']}")
            return True
            
        else:
            print(f"❌ Failed to create release: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error creating release: {e}")
        return False

if __name__ == "__main__":
    print("🔧 NITROTOOLS GitHub Release Creator")
    print("=" * 40)
    create_github_release()
