#!/usr/bin/env python3
"""
Waydroid Image URL Updater
Updates the spec file with the latest Waydroid image URLs from SourceForge
"""

import os
import re
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from html.parser import HTMLParser

# Configuration
SPEC_FILE = "waydroid-image.spec"
SOURCEFORGE_BASE = "https://sourceforge.net"
WAYDROID_FILES_BASE = f"{SOURCEFORGE_BASE}/projects/waydroid/files/images"

# SourceForge directory structure
IMAGE_DIRS = {
    # System images
    "SYS_VANILLA_X86_64_20": "system/lineage/waydroid_x86_64/lineage-20.*VANILLA.*x86_64.*system.zip",
    "SYS_GAPPS_X86_64_20": "system/lineage/waydroid_x86_64/lineage-20.*GAPPS.*x86_64.*system.zip",
    "SYS_VANILLA_ARM64_20": "system/lineage/waydroid_arm64/lineage-20.*VANILLA.*arm64.*system.zip",
    "SYS_GAPPS_ARM64_20": "system/lineage/waydroid_arm64/lineage-20.*GAPPS.*arm64.*system.zip",
    "SYS_VANILLA_X86_64_18": "system/lineage/waydroid_x86_64/lineage-18.*VANILLA.*x86_64.*system.zip",
    "SYS_GAPPS_X86_64_18": "system/lineage/waydroid_x86_64/lineage-18.*GAPPS.*x86_64.*system.zip",
    "SYS_VANILLA_ARM64_18": "system/lineage/waydroid_arm64/lineage-18.*VANILLA.*arm64.*system.zip",
    "SYS_GAPPS_ARM64_18": "system/lineage/waydroid_arm64/lineage-18.*GAPPS.*arm64.*system.zip",
    
    # Vendor images
    "VENDOR_X86_64_20": "vendor/waydroid_x86_64/lineage-20.*waydroid_x86_64.*vendor.zip",
    "VENDOR_ARM64_20": "vendor/waydroid_arm64/lineage-20.*waydroid_arm64.*vendor.zip",
    "VENDOR_X86_64_18": "vendor/waydroid_x86_64/lineage-18.*waydroid_x86_64.*vendor.zip",
    "VENDOR_ARM64_18": "vendor/waydroid_arm64/lineage-18.*waydroid_arm64.*vendor.zip",
}

class SourceForgeParser(HTMLParser):
    """Parser for SourceForge directory listings"""
    def __init__(self):
        super().__init__()
        self.files = []
        self.in_file_link = False
        self.current_file = None
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and '/files/images/' in value and value.endswith('.zip/download'):
                    # Extract filename from the URL
                    match = re.search(r'/([^/]+\.zip)/download$', value)
                    if match:
                        self.files.append(match.group(1))
                        
    def get_files(self):
        return self.files

def fetch_directory_listing(path):
    """Fetch and parse SourceForge directory listing"""
    url = f"{WAYDROID_FILES_BASE}/{path}/"
    print(f"Fetching directory: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            
        parser = SourceForgeParser()
        parser.feed(html)
        files = parser.get_files()
        
        print(f"  Found {len(files)} files in {path}")
        return files
        
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []

def find_latest_file(directory, pattern):
    """Find the latest file matching pattern in directory"""
    files = fetch_directory_listing(directory)
    
    # Convert pattern to regex
    regex_pattern = pattern.split('/')[-1]  # Get just the filename pattern
    regex_pattern = regex_pattern.replace('*', '.*').replace('?', '.')
    regex_pattern = f"^{regex_pattern}$"
    
    matching_files = []
    for file in files:
        if re.match(regex_pattern, file, re.IGNORECASE):
            matching_files.append(file)
            
    if not matching_files:
        print(f"  No files matching pattern: {pattern}")
        return None
        
    # Sort by date in filename (format: YYYYMMDD)
    def extract_date(filename):
        match = re.search(r'(\d{8})', filename)
        return match.group(1) if match else '00000000'
    
    matching_files.sort(key=extract_date, reverse=True)
    latest = matching_files
    print(f"  Latest match: {latest}")
    
    return latest

def get_download_url(directory, filename):
    """Construct the download URL for a file"""
    return f"{WAYDROID_FILES_BASE}/{directory}/{filename}/download"

def extract_version_from_files(file_urls):
    """Extract version (date) from the latest files"""
    dates = []
    for url in file_urls.values():
        if url:
            match = re.search(r'(\d{8})', url)
            if match:
                dates.append(match.group(1))
    
    if dates:
        # Return the most recent date
        return max(dates)
    else:
        # Fallback to current date
        return datetime.now().strftime('%Y%m%d')

def update_spec_file(image_urls, version):
    """Update the spec file with new URLs and version"""
    if not os.path.exists(SPEC_FILE):
        print(f"Error: {SPEC_FILE} not found!")
        return False
    
    try:
        # Read the spec file
        with open(SPEC_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update version
        content = re.sub(r'@VERSION@', version, content)
        
        # Update each URL placeholder
        updated_count = 0
        for key, url in image_urls.items():
            if url:
                # Replace the placeholder with the actual URL
                placeholder = f"@{key}@"
                if placeholder in content:
                    content = content.replace(placeholder, url)
                    updated_count += 1
                    print(f"  Updated {key}")
                else:
                    print(f"  Warning: Placeholder {placeholder} not found in spec file")
        
        # Write updated content
        with open(SPEC_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully updated {SPEC_FILE} with {updated_count} URLs")
        return True
        
    except Exception as e:
        print(f"Error updating {SPEC_FILE}: {e}")
        return False

def generate_spec_placeholders():
    """Generate a spec file template with placeholders"""
    template = """# waydroid-image.spec
# Auto-generated on {timestamp}
# Version: @VERSION@

%global _waydroid_image_dir %{{_datadir}}/waydroid-extra/images

# Define package details based on flavor
%if "%{{?_flavor}}" == "lineage-20-gapps"
  %define os_version 20
  %define os_type gapps
  %define flavor_descr LineageOS 20 with Google Apps (GAPPS)
%elseif "%{{?_flavor}}" == "lineage-20-vanilla"
  %define os_version 20
  %define os_type vanilla
  %define flavor_descr LineageOS 20 Vanilla (AOSP)
%elseif "%{{?_flavor}}" == "lineage-18-gapps"
  %define os_version 18
  %define os_type gapps
  %define flavor_descr LineageOS 18.1 with Google Apps (GAPPS)
%else
  %define _flavor lineage-18-vanilla
  %define os_version 18
  %define os_type vanilla
  %define flavor_descr LineageOS 18.1 Vanilla (AOSP)
%endif

Name:           waydroid-image-%{{_flavor}}
Version:        @VERSION@
Release:        0
Summary:        %{{flavor_descr}} images for Waydroid

# Source URLs - will be replaced with actual URLs
Source0:        @SYS_VANILLA_X86_64_20@
Source1:        @SYS_GAPPS_X86_64_20@
Source2:        @VENDOR_X86_64_20@
Source3:        @SYS_VANILLA_ARM64_20@
Source4:        @SYS_GAPPS_ARM64_20@
Source5:        @VENDOR_ARM64_20@
Source10:       @SYS_VANILLA_X86_64_18@
Source11:       @SYS_GAPPS_X86_64_18@
Source12:       @VENDOR_X86_64_18@
Source13:       @SYS_VANILLA_ARM64_18@
Source14:       @SYS_GAPPS_ARM64_18@
Source15:       @VENDOR_ARM64_18@

# Rest of spec file...
""".format(timestamp=datetime.now().isoformat())
    
    return template

def main():
    """Main function"""
    print("=== Waydroid Image URL Updater ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Looking for spec file: {SPEC_FILE}")
    
    # If spec file doesn't exist, create a template
    if not os.path.exists(SPEC_FILE):
        print(f"Creating template {SPEC_FILE}...")
        with open(SPEC_FILE, 'w') as f:
            f.write(generate_spec_placeholders())
        print(f"Template created. Please review and customize {SPEC_FILE}")
    
    # Find latest image URLs
    print("\n=== Scanning SourceForge for latest images ===")
    image_urls = {}
    
    for key, pattern in IMAGE_DIRS.items():
        print(f"\nSearching for {key}...")
        
        # Extract directory and filename pattern
        parts = pattern.split('/')
        directory = '/'.join(parts[:-1])
        
        # Find the latest file
        latest_file = find_latest_file(directory, pattern)
        
        if latest_file:
            url = get_download_url(directory, latest_file)
            image_urls[key] = url
            print(f"  URL: {url}")
        else:
            print(f"  WARNING: No file found for {key}")
            image_urls[key] = None
    
    # Extract version from the latest files
    version = extract_version_from_files(image_urls)
    print(f"\n=== Using version: {version} ===")
    
    # Count successful URLs
    found_count = sum(1 for url in image_urls.values() if url)
    print(f"\nFound {found_count}/{len(IMAGE_DIRS)} image URLs")
    
    if found_count == 0:
        print("ERROR: No image URLs found!")
        print("This might be due to:")
        print("  1. SourceForge is down or blocking requests")
        print("  2. The directory structure has changed")
        print("  3. Network connectivity issues")
        sys.exit(1)
    
    # Update spec file
    print(f"\n=== Updating {SPEC_FILE} ===")
    if update_spec_file(image_urls, version):
        print("\n=== Update completed successfully ===")
        
        # Print summary
        print("\nSummary:")
        print(f"  Version: {version}")
        print(f"  Updated URLs: {found_count}")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        
        # Save URLs to a JSON file for reference
        urls_file = "waydroid-urls.json"
        with open(urls_file, 'w') as f:
            json.dump({
                'version': version,
                'timestamp': datetime.now().isoformat(),
                'urls': image_urls
            }, f, indent=2)
        print(f"  URL list saved to: {urls_file}")
        
        sys.exit(0)
    else:
        print("\n=== Update failed ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
