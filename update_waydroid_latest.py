#!/usr/bin/env python3
"""
Waydroid Image URL Updater
Updates the spec file with the latest Waydroid image URLs from SourceForge
by parsing the HTML directory listings using curl to avoid 403 errors.
"""

import os
import re
import sys
import json
import subprocess
import shlex
from datetime import datetime

# Configuration
SPEC_FILE_TEMPLATE = "waydroid-image.spec.template"
SPEC_FILE_OUTPUT = "waydroid-image.spec"
SOURCEFORGE_BASE = "https://sourceforge.net"
WAYDROID_FILES_BASE = f"{SOURCEFORGE_BASE}/projects/waydroid/files/images"
# A standard browser user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# SourceForge directory structure and regex patterns
# Format: "PLACEHOLDER": ("path/to/directory", r"filename-regex-pattern")
# Updated to use MAINLINE vendor for all builds as requested.
IMAGE_DIRS = {
    # System images
    "SYS_VANILLA_X86_64_20": ("system/lineage/waydroid_x86_64", r"lineage-20.0-\d{8}-VANILLA-waydroid_x86_64-system.zip"),
    "SYS_GAPPS_X86_64_20": ("system/lineage/waydroid_x86_64", r"lineage-20.0-\d{8}-GAPPS-waydroid_x86_64-system.zip"),
    "SYS_VANILLA_ARM64_20": ("system/lineage/waydroid_arm64", r"lineage-20.0-\d{8}-VANILLA-waydroid_arm64-system.zip"),
    "SYS_GAPPS_ARM64_20": ("system/lineage/waydroid_arm64", r"lineage-20.0-\d{8}-GAPPS-waydroid_arm64-system.zip"),
    "SYS_VANILLA_X86_64_18": ("system/lineage/waydroid_x86_64", r"lineage-18.1-\d{8}-VANILLA-waydroid_x86_64-system.zip"),
    "SYS_GAPPS_X86_64_18": ("system/lineage/waydroid_x86_64", r"lineage-18.1-\d{8}-GAPPS-waydroid_x86_64-system.zip"),
    "SYS_VANILLA_ARM64_18": ("system/lineage/waydroid_arm64", r"lineage-18.1-\d{8}-VANILLA-waydroid_arm64-system.zip"),
    "SYS_GAPPS_ARM64_18": ("system/lineage/waydroid_arm64", r"lineage-18.1-\d{8}-GAPPS-waydroid_arm64-system.zip"),

    # Vendor images
    "VENDOR_X86_64_20": ("vendor/waydroid_x86_64", r"lineage-20.0-\d{8}-MAINLINE-waydroid_x86_64-vendor.zip"),
    "VENDOR_ARM64_20": ("vendor/waydroid_arm64", r"lineage-20.0-\d{8}-MAINLINE-waydroid_arm64-vendor.zip"), # Use MAINLINE
    "VENDOR_X86_64_18": ("vendor/waydroid_x86_64", r"lineage-18.1-\d{8}-MAINLINE-waydroid_x86_64-vendor.zip"),
    "VENDOR_ARM64_18": ("vendor/waydroid_arm64", r"lineage-18.1-\d{8}-MAINLINE-waydroid_arm64-vendor.zip"), # Use MAINLINE
}

def fetch_directory_listing(path):
    """Fetch and parse SourceForge directory listing HTML using curl"""
    url = f"{WAYDROID_FILES_BASE}/{path}/"
    print(f"  Fetching {url}")
    try:
        # Use curl to bypass anti-bot measures
        cmd = ["curl", "-L", "-A", USER_AGENT, url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"  Error fetching {url} with curl: {e}")
        print(f"  STDERR: {e.stderr}")
        return ""
    except FileNotFoundError:
        print("  Error: 'curl' command not found. Please install curl.")
        sys.exit(1)
    except Exception as e:
        print(f"  An unexpected error occurred: {e}")
        return ""


def find_latest_file(directory, pattern_regex):
    """Find the latest file matching pattern in directory"""
    html = fetch_directory_listing(directory)
    if not html:
        return None

    # Regex to find all .zip download links
    # This captures the relative path, e.g., /projects/waydroid/files/images/.../file.zip
    all_links = re.findall(r'href="([^"]+\.zip)/download"', html)
    
    if not all_links:
        print(f"  No .zip links found in directory: {directory}")
        return None

    matching_files = []
    compiled_regex = re.compile(f"^{pattern_regex}$", re.IGNORECASE)
    
    for link_path in all_links:
        filename = link_path.split('/')[-1]
        
        if compiled_regex.match(filename):
            # Extract date for sorting
            date_match = re.search(r'(\d{8})', filename)
            if date_match:
                date_str = date_match.group(1)
                full_url = f"{SOURCEFORGE_BASE}{link_path}/download"
                matching_files.append((date_str, full_url))
            else:
                print(f"  Warning: Matched file {filename} has no date.")
                
    if not matching_files:
        print(f"  No files matching pattern: {pattern_regex}")
        return None
        
    # Sort by date (most recent first)
    matching_files.sort(key=lambda x: x[0], reverse=True)
    
    latest_url = matching_files[0][1] # Get the URL of the newest file
    print(f"  Latest match: {latest_url.split('/')[-2]}")
    
    return latest_url

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
                    # If a URL wasn't found, replace placeholder with a comment
                    content = content.replace(placeholder, f"# {key} - Not Found")
                    print(f"  Warning: No URL found for {placeholder}. Commenting out.")
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
    
    # Check if template file exists, if not, rename .spec
    if not os.path.exists(SPEC_FILE_TEMPLATE) and os.path.exists(SPEC_FILE_OUTPUT):
         print(f"Template file '{SPEC_FILE_TEMPLATE}' not found.")
         print(f"Renaming '{SPEC_FILE_OUTPUT}' to '{SPEC_FILE_TEMPLATE}' to use as template.")
         os.rename(SPEC_FILE_OUTPUT, SPEC_FILE_TEMPLATE)
    elif not os.path.exists(SPEC_FILE_TEMPLATE):
        print(f"ERROR: '{SPEC_FILE_TEMPLATE}' not found. Please create it.")
        print("Your 'waydroid-image.spec' file in the repo should be this template.")
        sys.exit(1)

    # Find latest image URLs
    print("\n=== Scanning SourceForge for latest images ===")
    image_urls = {}
    
    for key, (directory, pattern) in IMAGE_DIRS.items():
        print(f"\nSearching for {key}...")
        
        # Find the latest file
        latest_url = find_latest_file(directory, pattern)
        image_urls[key] = latest_url
        if latest_url:
            print(f"  URL: {latest_url}")
        else:
            print(f"  WARNING: No file found for {key}")
    
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

