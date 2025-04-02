"""
Page navigator module for handling navigation and screenshot capture.
"""

import os
import time
import logging
import re
from urllib.parse import urlparse
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class PageNavigator:
    """
    A class for navigating web pages and capturing screenshots.
    
    This class handles navigation to URLs, waiting for page load,
    and capturing screenshots of the rendered pages.
    """
    
    def __init__(self, browser, navigation_timeout=30000, wait_after_load=2000):
        """
        Initialize the page navigator.
        
        Args:
            browser (Browser): The browser instance to use for navigation.
            navigation_timeout (int): Timeout for navigation in milliseconds.
            wait_after_load (int): Time to wait after page load in milliseconds.
        """
        self.browser = browser
        self.navigation_timeout = navigation_timeout
        self.wait_after_load = wait_after_load
    
    def navigate_to_url(self, page, url):
        """
        Navigate to a URL and return information about the page.
        
        Args:
            page (playwright.sync_api.Page): The page to navigate with.
            url (str): The URL to navigate to.
            
        Returns:
            dict: Information about the page, including ID and title.
        """
        logger.info(f"Navigating to: {url}")
        
        try:
            # Navigate to the URL with timeout
            page.goto(url, timeout=self.navigation_timeout)
            
            # Wait for the page to be fully loaded
            page.wait_for_load_state('networkidle')
            
            # Wait a bit more to ensure dynamic content is loaded
            if self.wait_after_load > 0:
                page.wait_for_timeout(self.wait_after_load)
            
            # Get page title
            title = page.title()
            
            # Generate a page ID from the URL
            page_id = self._generate_page_id(url, title)
            
            logger.info(f"Navigation complete: {title} (ID: {page_id})")
            
            return {
                'id': page_id,
                'url': url,
                'title': title
            }
        
        except PlaywrightTimeoutError:
            logger.warning(f"Navigation timeout for URL: {url}")
            # Generate a fallback page ID
            page_id = self._generate_page_id(url, "Timeout")
            
            return {
                'id': page_id,
                'url': url,
                'title': "Navigation Timeout"
            }
        
        except Exception as e:
            logger.exception(f"Navigation error for URL {url}: {str(e)}")
            # Generate a fallback page ID
            page_id = self._generate_page_id(url, "Error")
            
            return {
                'id': page_id,
                'url': url,
                'title': f"Navigation Error: {str(e)}"
            }
    
    def _generate_page_id(self, url, title):
        """
        Generate a unique page ID from URL and title.
        
        Args:
            url (str): The URL of the page.
            title (str): The title of the page.
            
        Returns:
            str: A sanitized page ID.
        """
        # Parse the URL to get path
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Clean up the path
        if not path or path == '/':
            page_name = 'home'
        else:
            # Remove leading/trailing slashes and replace internal ones
            page_name = path.strip('/').replace('/', '_')
        
        # Add a slug from the title (if available)
        if title and not title.lower() in ['timeout', 'error']:
            # Extract first few words from title and sanitize
            title_slug = re.sub(r'[^a-zA-Z0-9]', '_', title)
            title_slug = re.sub(r'_+', '_', title_slug)  # Replace multiple underscores with a single one
            title_slug = title_slug[:30].strip('_').lower()  # Limit length
            
            if title_slug:
                page_name = f"{page_name}_{title_slug}"
        
        # Add query parameters if they exist (simplified)
        if parsed_url.query:
            query_hash = str(abs(hash(parsed_url.query)) % 1000)
            page_name = f"{page_name}_q{query_hash}"
        
        return page_name
    
    def capture_screenshot(self, page, file_path):
        """
        Capture a screenshot of the current page.
        
        Args:
            page (playwright.sync_api.Page): The page to capture.
            file_path (str): The path to save the screenshot to.
            
        Returns:
            bool: True if the screenshot was captured successfully, False otherwise.
        """
        logger.info(f"Capturing screenshot to: {file_path}")
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Take the screenshot
            page.screenshot(path=file_path, full_page=True)
            
            logger.info(f"Screenshot captured: {file_path}")
            return True
        
        except Exception as e:
            logger.exception(f"Screenshot capture error: {str(e)}")
            return False
    
    def wait_for_login_completion(self, page, timeout=300000, check_interval=1000):
        """
        Wait for the user to complete manual login.
        
        This method monitors changes in the URL and page content to detect
        when a user has successfully logged in.
        
        Args:
            page (playwright.sync_api.Page): The page to monitor.
            timeout (int): Maximum time to wait in milliseconds.
            check_interval (int): Interval between checks in milliseconds.
            
        Returns:
            bool: True if login completion was detected, False on timeout.
        """
        logger.info("Waiting for manual login completion...")
        
        # Store initial URL and content hash
        initial_url = page.url
        
        # Function to check if substantial changes have occurred
        def detect_login_completion():
            """Check if login appears to be complete based on URL changes."""
            current_url = page.url
            
            # Check for URL change that suggests successful login
            if current_url != initial_url and '/dashboard' in current_url:
                return True
            
            # User can press Enter key to signal login completion
            try:
                # Check for a dashboard element that indicates successful login
                return page.is_visible('text=Dashboard')
            except:
                return False
        
        # Wait for changes that suggest login is complete
        start_time = time.time()
        end_time = start_time + (timeout / 1000)
        
        while time.time() < end_time:
            if detect_login_completion():
                elapsed = time.time() - start_time
                logger.info(f"Login completion detected after {elapsed:.1f} seconds")
                return True
            
            # Wait before checking again
            page.wait_for_timeout(check_interval)
        
        logger.warning(f"Login wait timed out after {timeout/1000} seconds")
        return False 