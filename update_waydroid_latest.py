#!/usr/bin/env python3
"""
Waydroid Image URL Updater
Updates the spec file with the latest Waydroid image URLs from SourceForge
by parsing the project's RSS feeds, which is more reliable than HTML scraping.
"""

import os
import re
import sys
import json
import subprocess
import shlex
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

# Configuration
SPEC_FILE_TEMPLATE = "waydroid-image.spec.template"
SPEC_FILE_OUTPUT = "waydroid-image.spec"
SOURCEFORGE_BASE = "https://sourceforge.net"
WAYDROID_PROJECT = "waydroid"
# A standard browser user-agent (still needed for curl)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# SourceForge directory structure relative to /projects/waydroid/files/
# and regex patterns for filenames.
# Format: "PLACEHOLDER": ("path/relative/to/files", r"filename-regex-pattern")
IMAGE_DIRS = {
    # System images
    "SYS_VANILLA_X86_64_20": ("images/system/lineage/waydroid_x86_64", r"lineage-20.0-\d{8}-VANILLA-waydroid_x86_64-system.zip"),
    "SYS_GAPPS_X86_64_20": ("images/system/lineage/waydroid_x86_64", r"lineage-20.0-\d{8}-GAPPS-waydroid_x86_64-system.zip"),
    "SYS_VANILLA_ARM64_20": ("images/system/lineage/waydroid_arm64", r"lineage-20.0-\d{8}-VANILLA-waydroid_arm64-system.zip"),
    "SYS_GAPPS_ARM64_20": ("images/system/lineage/waydroid_arm64", r"lineage-20.0-\d{8}-GAPPS-waydroid_arm64-system.zip"),
    "SYS_VANILLA_X86_64_18": ("images/system/lineage/waydroid_x86_64", r"lineage-18.1-\d{8}-VANILLA-waydroid_x86_64-system.zip"),
    "SYS_GAPPS_X86_64_18": ("images/system/lineage/waydroid_x86_64", r"lineage-18.1-\d{8}-GAPPS-waydroid_x86_64-system.zip"),
    "SYS_VANILLA_ARM64_18": ("images/system/lineage/waydroid_arm64", r"lineage-18.1-\d{8}-VANILLA-waydroid_arm64-system.zip"),
    "SYS_GAPPS_ARM64_18": ("images/system/lineage/waydroid_arm64", r"lineage-18.1-\d{8}-GAPPS-waydroid_arm64-system.zip"),

    # Vendor images
    "VENDOR_X86_64_20": ("images/vendor/waydroid_x86_64", r"lineage-20.0-\d{8}-MAINLINE-waydroid_x86_64-vendor.zip"),
    "VENDOR_ARM64_20": ("images/vendor/waydroid_arm64", r"lineage-20.0-\d{8}-MAINLINE-waydroid_arm64-vendor.zip"),
    "VENDOR_X86_64_18": ("images/vendor/waydroid_x86_64", r"lineage-18.1-\d{8}-MAINLINE-waydroid_x86_64-vendor.zip"),
    "VENDOR_ARM64_18": ("images/vendor/waydroid_arm64", r"lineage-18.1-\d{8}-MAINLINE-waydroid_arm64-vendor.zip"),
}

def fetch_rss_feed(path):
    """Fetch and return the content of the SourceForge RSS feed for a path."""
    # Construct RSS feed URL. Example: https://sourceforge.net/projects/waydroid/rss?path=/images/system/lineage/waydroid_x86_64
    rss_url = f"{SOURCEFORGE_BASE}/projects/{WAYDROID_PROJECT}/rss?path=/{path}"
    print(f"  Fetching RSS Feed: {rss_url}")
    try:
        # Use curl to fetch the RSS feed
        cmd = ["curl", "--fail", "-L", "-A", USER_AGENT, rss_url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"  Error fetching RSS {rss_url} with curl: {e}")
        print(f"  STDERR: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  Error: curl command timed out fetching RSS {rss_url}")
        return None
    except FileNotFoundError:
        print("  Error: 'curl' command not found. Please install curl.")
        sys.exit(1)
    except Exception as e:
        print(f"  An unexpected error occurred during RSS fetch: {e}")
        return None

def find_latest_file_in_rss(path, filename_pattern_regex):
    """Find the latest file matching pattern in the directory's RSS feed."""
    rss_content = fetch_rss_feed(path)
    if not rss_content:
        return None

    try:
        root = ET.fromstring(rss_content)
        namespace = {'media': 'http://search.yahoo.com/mrss/'} # Namespace for media:content
        items = []

        # Iterate through each item (file) in the RSS feed
        for item in root.findall('.//item'):
            title_tag = item.find('title')
            link_tag = item.find('link')
            pubDate_tag = item.find('pubDate')
            # Look for media:content tag which often has the direct download URL
            media_content = item.find('media:content', namespace)

            if title_tag is not None and title_tag.text:
                filename = title_tag.text.split('/')[-1] # Get filename from title

                # Check if filename matches the required pattern
                if re.match(f"^{filename_pattern_regex}$", filename, re.IGNORECASE):
                    pubDate = None
                    if pubDate_tag is not None and pubDate_tag.text:
                        try:
                            # Parse RFC 822 date format
                            pubDate = parsedate_to_datetime(pubDate_tag.text)
                        except Exception as e:
                            print(f"  Warning: Could not parse pubDate '{pubDate_tag.text}': {e}")

                    # Prefer media:content url if available, otherwise use link tag
                    url = None
                    if media_content is not None and media_content.get('url'):
                        url = media_content.get('url')
                        # Ensure it ends with /download for consistency if needed, though direct link is better
                        if '/download' not in url:
                             # Check if it looks like a direct file link already
                             if not url.endswith(filename):
                                 # If it's not the direct file link, try appending /download
                                 url = url.replace(f"/{filename}", f"/{filename}/download")

                    elif link_tag is not None and link_tag.text:
                        url = link_tag.text
                        # Ensure link ends with /download
                        if not url.endswith('/download'):
                            url = url.rstrip('/') + '/download'

                    if url and pubDate:
                        items.append({'filename': filename, 'url': url, 'pubDate': pubDate})
                    elif url:
                        # Fallback if pubDate parsing failed, use file date
                        date_match = re.search(r'(\d{8})', filename)
                        if date_match:
                             try:
                                 file_date = datetime.strptime(date_match.group(1), '%Y%m%d')
                                 items.append({'filename': filename, 'url': url, 'pubDate': file_date})
                             except ValueError:
                                  print(f"  Warning: Could not parse date from filename {filename}")
                        else:
                            print(f"  Warning: No pubDate or parsable date in filename for {filename}")


        if not items:
            print(f"  No files matching pattern '{filename_pattern_regex}' found in RSS feed for path '{path}'.")
            return None

        # Sort items by publication date, newest first
        items.sort(key=lambda x: x['pubDate'], reverse=True)

        latest_item = items[0]
        print(f"  Latest match from RSS: {latest_item['filename']} ({latest_item['pubDate']})")
        return latest_item['url']

    except ET.ParseError as e:
        print(f"  Error parsing RSS feed XML for path '{path}': {e}")
        # print("--- RSS Content Snippet ---") # Debugging
        # print(rss_content[:1000])
        # print("--- End RSS Snippet ---")
        return None
    except Exception as e:
        print(f"  An unexpected error occurred during RSS parsing: {e}")
        return None


# --- Functions extract_version_from_files, update_spec_file, and main are adapted slightly ---

def extract_version_from_files(file_urls):
    """Extract version (date) from the latest files."""
    dates = []
    for url in file_urls.values():
        if url:
            # Find the first 8-digit number in the URL (likely in filename part)
            match = re.search(r'(\d{8})', url)
            if match:
                dates.append(match.group(1))

    if dates:
        return max(dates) # Return the most recent date
    else:
        # Fallback if no dates found in any URL
        return datetime.now().strftime('%Y%m%d')

def update_spec_file(image_urls, version, timestamp):
    """Update the spec file with new URLs and version."""
    if not os.path.exists(SPEC_FILE_TEMPLATE):
        print(f"Error: Template file {SPEC_FILE_TEMPLATE} not found!")
        return False

    try:
        with open(SPEC_FILE_TEMPLATE, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('@TIMESTAMP@', timestamp)
        content = content.replace('@VERSION@', version)

        updated_count = 0
        missing_placeholders = []
        for key, url in image_urls.items():
            placeholder = f"@{key}@"
            if placeholder in content:
                if url:
                    # Make sure the URL has /download if it's not a direct media link
                    if '/download' not in url and WAYDROID_PROJECT in url and '/files/' in url:
                         # Basic check to avoid adding /download to direct links if possible
                         filename_part = url.split('/')[-1]
                         if '.zip' in filename_part: # Check if the last part seems to be the zip file
                              # Assume it needs /download
                              url = url.rstrip('/') + '/download'

                    content = content.replace(placeholder, url)
                    updated_count += 1
                    print(f"  Replaced {placeholder}")
                else:
                    content = content.replace(placeholder, f"# {key} - Not Found in RSS")
                    print(f"  Warning: No URL found for {placeholder}. Commenting out.")
            else:
                missing_placeholders.append(placeholder)

        if missing_placeholders:
             print(f"\n  Warning: The following placeholders were NOT found in {SPEC_FILE_TEMPLATE}:")
             for ph in missing_placeholders:
                  print(f"    {ph}")

        with open(SPEC_FILE_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nSuccessfully updated {SPEC_FILE_OUTPUT} with {updated_count} URLs")
        return True

    except Exception as e:
        print(f"Error updating {SPEC_FILE_OUTPUT}: {e}")
        return False

def main():
    """Main function"""
    print("=== Waydroid Image URL Updater (RSS Version) ===")

    if not os.path.exists(SPEC_FILE_TEMPLATE) and os.path.exists(SPEC_FILE_OUTPUT):
         print(f"Template file '{SPEC_FILE_TEMPLATE}' not found.")
         print(f"Renaming '{SPEC_FILE_OUTPUT}' to '{SPEC_FILE_TEMPLATE}' to use as template.")
         try:
            os.rename(SPEC_FILE_OUTPUT, SPEC_FILE_TEMPLATE)
         except OSError as e:
             print(f"Error renaming file: {e}")
             sys.exit(1)
    elif not os.path.exists(SPEC_FILE_TEMPLATE):
        print(f"ERROR: Template file '{SPEC_FILE_TEMPLATE}' not found.")
        print(f"Ensure your spec file template exists and is named correctly.")
        sys.exit(1)

    print("\n=== Scanning SourceForge RSS feeds for latest images ===")
    image_urls = {}

    # Use the new RSS parsing function
    for key, (directory_path, filename_pattern) in IMAGE_DIRS.items():
        print(f"\nSearching for {key} in path '{directory_path}'...")
        latest_url = find_latest_file_in_rss(directory_path, filename_pattern)
        image_urls[key] = latest_url
        if not latest_url:
            print(f"  WARNING: No file found for {key}")
        # No need to print URL here, find_latest_file_in_rss does it

    version = extract_version_from_files(image_urls)
    timestamp = datetime.now().isoformat()
    print(f"\n=== Using version: {version} ===")

    found_count = sum(1 for url in image_urls.values() if url)
    print(f"\nFound {found_count}/{len(IMAGE_DIRS)} image URLs via RSS")

    if found_count == 0:
        print("\nERROR: No image URLs found via RSS feeds! Exiting.")
        print("Possible reasons: RSS feeds unavailable, path changes, or filename pattern mismatch.")
        sys.exit(1)

    print(f"\n=== Updating {SPEC_FILE_OUTPUT} from {SPEC_FILE_TEMPLATE} ===")
    if update_spec_file(image_urls, version, timestamp):
        print("\n=== Update completed successfully ===")
        urls_file = "waydroid-urls.json"
        try:
            with open(urls_file, 'w') as f:
                json.dump({
                    'version': version,
                    'timestamp': timestamp,
                    'urls': image_urls
                }, f, indent=2)
            print(f"  URL list saved to: {urls_file}")
        except IOError as e:
            print(f"  Warning: Could not save URL list to {urls_file}: {e}")
    else:
        print("\n=== Update failed ===")
        sys.exit(1)

if __name__ == "__main__":
    main()

