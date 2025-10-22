#!/usr/bin/env python3
"""
Waydroid Image URL Updater
Updates the spec file with the latest Waydroid image URLs from SourceForge
using the JSON API.
"""

import os
import re
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Configuration
SPEC_FILE_TEMPLATE = "waydroid-image.spec.template"
SPEC_FILE_OUTPUT = "waydroid-image.spec"
SOURCEFORGE_BASE = "https://sourceforge.net"
WAYDROID_FILES_BASE = f"{SOURCEFORGE_BASE}/projects/waydroid/files/images"

# SourceForge directory structure and regex patterns
IMAGE_DIRS = {
    # System images
    "SYS_VANILLA_X86_64_20": "system/lineage/waydroid_x86_64/lineage-20.0-.*-VANILLA-waydroid_x86_64-system.zip",
    "SYS_GAPPS_X86_64_20": "system/lineage/waydroid_x86_64/lineage-20.0-.*-GAPPS-waydroid_x86_64-system.zip",
    "SYS_VANILLA_ARM64_20": "system/lineage/waydroid_arm64/lineage-20.0-.*-VANILLA-waydroid_arm64-system.zip",
    "SYS_GAPPS_ARM64_20": "system/lineage/waydroid_arm64/lineage-20.0-.*-GAPPS-waydroid_arm64-system.zip",
    "SYS_VANILLA_X86_64_18": "system/lineage/waydroid_x86_64/lineage-18.1-.*-VANILLA-waydroid_x86_64-system.zip",
    "SYS_GAPPS_X86_64_18": "system/lineage/waydroid_x86_64/lineage-18.1-.*-GAPPS-waydroid_x86_64-system.zip",
    "SYS_VANILLA_ARM64_18": "system/lineage/waydroid_arm64/lineage-18.1-.*-VANILLA-waydroid_arm64-system.zip",
    "SYS_GAPPS_ARM64_18": "system/lineage/waydroid_arm64/lineage-18.1-.*-GAPPS-waydroid_arm64-system.zip",

    # Vendor images
    "VENDOR_X86_64_20": "vendor/waydroid_x86_64/lineage-20.0-.*-MAINLINE-waydroid_x86_64-vendor.zip",
    "VENDOR_ARM64_20": "vendor/waydroid_arm64/lineage-20.0-.*-HALIUM_13-waydroid_arm64-vendor.zip", # Prefer HALIUM 13 for L20
    "VENDOR_X86_64_18": "vendor/waydroid_x86_64/lineage-18.1-.*-MAINLINE-waydroid_x86_64-vendor.zip",
    "VENDOR_ARM64_18": "vendor/waydroid_arm64/lineage-18.1-.*-HALIUM_11-waydroid_arm64-vendor.zip", # Prefer HALIUM 11 for L18
}

def fetch_directory_json(path):
    """Fetch all file listings from SourceForge JSON API, handling pagination."""
    all_files = []
    page = 1
    while True:
        url = f"{WAYDROID_FILES_BASE}/{path}/files.json?page={page}"
        print(f"  Fetching {url}")
        try:
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    print(f"  Error: HTTP {response.status}")
                    break
                data = json.load(response)
                
                if 'files' not in data or not data['files']:
                    break # No more files
                    
                all_files.extend(data['files'])
                
                # Check pagination
                if page >= data.get('pagination', {}).get('total_pages', 1):
                    break
                page += 1
                
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return [] # Return empty on error
            
    print(f"  Found {len(all_files)} total files in {path}")
    return all_files

def find_latest_file(directory, pattern):
    """Find the latest file matching pattern in directory using JSON data."""
    files = fetch_directory_json(directory)
    if not files:
        return None

    regex_pattern = pattern.split('/')[-1] # Get just the filename pattern
    regex_pattern = regex_pattern.replace('*', '.*').replace('?', '.')
    regex_pattern = f"^{regex_pattern}$"
    
    matching_files = []
    for file in files:
        if re.match(regex_pattern, file['name'], re.IGNORECASE):
            matching_files.append(file)
            
    if not matching_files:
        print(f"  No files matching pattern: {pattern}")
        return None
        
    # Sort by timestamp (most recent first)
    matching_files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    latest_file = matching_files[0]['name']
    print(f"  Latest match: {latest_file}")
    
    return latest_file

def get_download_url(directory, filename):
    """Construct the download URL for a file."""
    return f"{WAYDROID_FILES_BASE}/{directory}/{filename}/download"

def extract_version_from_files(file_urls):
    """Extract version (date) from the latest files."""
    dates = []
    for url in file_urls.values():
        if url:
            # Find the first 8-digit number
            match = re.search(r'(\d{8})', url)
            if match:
                dates.append(match.group(1))
    
    if dates:
        return max(dates) # Return the most recent date
    else:
        return datetime.now().strftime('%Y%m%d') # Fallback

def update_spec_file(image_urls, version, timestamp):
    """Update the spec file with new URLs and version."""
    if not os.path.exists(SPEC_FILE_TEMPLATE):
        print(f"Error: Template file {SPEC_FILE_TEMPLATE} not found!")
        print("Please create it first. It should contain placeholders like @VERSION@")
        return False
    
    try:
        # Read the template file
        with open(SPEC_FILE_TEMPLATE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Update timestamp and version
        content = content.replace('@TIMESTAMP@', timestamp)
        content = content.replace('@VERSION@', version)
        
        # Update each URL placeholder
        updated_count = 0
        for key, url in image_urls.items():
            placeholder = f"@{key}@"
            if placeholder in content:
                if url:
                    content = content.replace(placeholder, url)
                    updated_count += 1
                    print(f"  Replaced {placeholder}")
                else:
                    print(f"  Warning: No URL found for {placeholder}. Leaving it as is.")
            else:
                print(f"  Warning: Placeholder {placeholder} not found in template")
                
        # Write updated content to the output file
        with open(SPEC_FILE_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully updated {SPEC_FILE_OUTPUT} with {updated_count} URLs")
        return True
        
    except Exception as e:
        print(f"Error updating {SPEC_FILE_OUTPUT}: {e}")
        return False

def main():
    """Main function"""
    print("=== Waydroid Image URL Updater ===")
    
    # Rename waydroid-image.spec to waydroid-image.spec.template if it exists
    if os.path.exists("waydroid-image.spec") and not os.path.exists(SPEC_FILE_TEMPLATE):
        print(f"Renaming 'waydroid-image.spec' to '{SPEC_FILE_TEMPLATE}' to use as template.")
        os.rename("waydroid-image.spec", SPEC_FILE_TEMPLATE)

    # Find latest image URLs
    print("\n=== Scanning SourceForge for latest images ===")
    image_urls = {}
    
    for key, pattern in IMAGE_DIRS.items():
        print(f"\nSearching for {key}...")
        
        # Extract directory
        directory = '/'.join(pattern.split('/')[:-1])
        
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
    timestamp = datetime.now().isoformat()
    print(f"\n=== Using version: {version} ===")
    
    # Count successful URLs
    found_count = sum(1 for url in image_urls.values() if url)
    print(f"\nFound {found_count}/{len(IMAGE_DIRS)} image URLs")
    
    if found_count == 0:
        print("ERROR: No image URLs found! Exiting.")
        sys.exit(1)
    
    # Update spec file
    print(f"\n=== Updating {SPEC_FILE_OUTPUT} from {SPEC_FILE_TEMPLATE} ===")
    if update_spec_file(image_urls, version, timestamp):
        print("\n=== Update completed successfully ===")
        # Save URLs to a JSON file for reference
        urls_file = "waydroid-urls.json"
        with open(urls_file, 'w') as f:
            json.dump({
                'version': version,
                'timestamp': timestamp,
                'urls': image_urls
            }, f, indent=2)
        print(f"  URL list saved to: {urls_file}")
    else:
        print("\n=== Update failed ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
