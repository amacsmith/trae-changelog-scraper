#!/usr/bin/env python3
"""
Trae.ai Changelog Scraper
Fetches the changelog page, downloads images, and converts to markdown.
"""

import os
import re
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import html2text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CHANGELOG_URL = "https://www.trae.ai/changelog"
OUTPUT_DIR = Path("/app/output")
IMAGES_DIR = OUTPUT_DIR / "images"
MARKDOWN_FILE = OUTPUT_DIR / "changelog.md"
REQUEST_TIMEOUT = 30


def ensure_directories():
    """Create necessary directories if they don't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directories ensured: {OUTPUT_DIR}, {IMAGES_DIR}")


def fetch_page(url):
    """Fetch the changelog page content."""
    try:
        logger.info(f"Fetching page: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        logger.info(f"Page fetched successfully (status: {response.status_code})")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch page: {e}")
        raise


def download_image(img_url, img_name):
    """Download an image and save it locally."""
    try:
        logger.info(f"Downloading image: {img_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(img_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        img_path = IMAGES_DIR / img_name
        img_path.write_bytes(response.content)
        logger.info(f"Image saved: {img_path}")
        return f"images/{img_name}"
    except requests.RequestException as e:
        logger.error(f"Failed to download image {img_url}: {e}")
        return img_url  # Return original URL if download fails


def sanitize_filename(url):
    """Create a safe filename from a URL."""
    parsed = urlparse(url)
    path = parsed.path
    filename = os.path.basename(path)

    # If no filename in path, create one from the URL
    if not filename or '.' not in filename:
        filename = f"image_{abs(hash(url))}.jpg"

    # Sanitize the filename
    filename = re.sub(r'[^\w\-.]', '_', filename)
    return filename


def process_images(soup, base_url):
    """Download all images and update their URLs in the soup."""
    images = soup.find_all('img')
    logger.info(f"Found {len(images)} images to process")

    for img in images:
        src = img.get('src') or img.get('data-src')
        if not src:
            continue

        # Convert relative URLs to absolute
        img_url = urljoin(base_url, src)

        # Skip data URLs and SVGs
        if img_url.startswith('data:') or img_url.endswith('.svg'):
            continue

        # Download and update the image URL
        img_name = sanitize_filename(img_url)
        local_path = download_image(img_url, img_name)
        img['src'] = local_path


def html_to_markdown(html_content, base_url):
    """Convert HTML to markdown with image handling."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Process images first
    process_images(soup, base_url)

    # Configure html2text converter
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap text
    h.protect_links = True
    h.mark_code = True

    # Convert to markdown
    markdown = h.handle(str(soup))
    return markdown


def save_markdown(content):
    """Save the markdown content to a file."""
    try:
        # Add header with timestamp
        header = f"""# Trae.ai Changelog

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Source: {CHANGELOG_URL}

---

"""
        full_content = header + content

        MARKDOWN_FILE.write_text(full_content, encoding='utf-8')
        logger.info(f"Markdown saved: {MARKDOWN_FILE}")
        logger.info(f"File size: {MARKDOWN_FILE.stat().st_size} bytes")
    except Exception as e:
        logger.error(f"Failed to save markdown: {e}")
        raise


def run_git_command(command, cwd=None):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd or OUTPUT_DIR,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            logger.warning(f"Git command warning: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Failed to run git command {command}: {e}")
        return False, "", str(e)


def git_commit_and_push():
    """Commit and push changes to GitHub."""
    try:
        logger.info("Checking for changes to commit...")

        # Check if there are any changes
        success, stdout, _ = run_git_command(["git", "status", "--porcelain"])
        if not success or not stdout.strip():
            logger.info("No changes to commit")
            return

        # Add all changes
        logger.info("Adding changes to git...")
        run_git_command(["git", "add", "."])

        # Commit changes
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        commit_message = f"Update changelog - {timestamp}"
        logger.info(f"Committing: {commit_message}")
        run_git_command(["git", "commit", "-m", commit_message])

        # Push to GitHub
        logger.info("Pushing to GitHub...")
        success, stdout, stderr = run_git_command(["git", "push"])
        if success:
            logger.info("Successfully pushed to GitHub!")
        else:
            logger.error(f"Failed to push to GitHub: {stderr}")

    except Exception as e:
        logger.error(f"Git operations failed: {e}")


def main():
    """Main execution function."""
    try:
        logger.info("=" * 60)
        logger.info("Starting Trae.ai Changelog Scraper")
        logger.info("=" * 60)

        # Ensure output directories exist
        ensure_directories()

        # Fetch the page
        html_content = fetch_page(CHANGELOG_URL)

        # Convert to markdown with images
        logger.info("Converting HTML to markdown...")
        markdown_content = html_to_markdown(html_content, CHANGELOG_URL)

        # Save the result
        save_markdown(markdown_content)

        # Commit and push to GitHub
        git_commit_and_push()

        logger.info("=" * 60)
        logger.info("Scraping completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise


if __name__ == "__main__":
    main()
