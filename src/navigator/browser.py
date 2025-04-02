"""
Browser module for handling browser initialization and management.
"""

import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class Browser:
    """
    A class for managing the browser instance.
    
    This class handles browser initialization, configuration, and cleanup.
    It uses Playwright to control the browser.
    """
    
    def __init__(self, headless=False, browser_type='chromium', viewport_size=None):
        """
        Initialize the browser manager.
        
        Args:
            headless (bool): Whether to run the browser in headless mode.
            browser_type (str): Type of browser to use ('chromium', 'firefox', or 'webkit').
            viewport_size (dict): Dictionary with 'width' and 'height' keys for viewport size.
        """
        self.headless = headless
        self.browser_type = browser_type
        self.viewport_size = viewport_size or {'width': 1280, 'height': 800}
        
        self.playwright = None
        self.browser = None
        self.context = None
    
    def start(self):
        """
        Start the browser and return a new page.
        
        Returns:
            playwright.sync_api.Page: A new browser page.
        """
        logger.info(f"Starting {self.browser_type} browser (headless={self.headless})")
        
        try:
            self.playwright = sync_playwright().start()
            
            # Select browser based on type
            if self.browser_type == 'chromium':
                browser_factory = self.playwright.chromium
            elif self.browser_type == 'firefox':
                browser_factory = self.playwright.firefox
            elif self.browser_type == 'webkit':
                browser_factory = self.playwright.webkit
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Launch browser
            self.browser = browser_factory.launch(headless=self.headless)
            
            # Create a new context with viewport size
            self.context = self.browser.new_context(
                viewport=self.viewport_size,
                record_video_dir="videos/" if not self.headless else None
            )
            
            # Create and return a new page
            page = self.context.new_page()
            logger.info("Browser started successfully")
            return page
        
        except Exception as e:
            logger.exception(f"Failed to start browser: {str(e)}")
            self.stop()
            raise
    
    def stop(self):
        """
        Clean up browser resources.
        """
        logger.info("Stopping browser...")
        
        # Close context
        if self.context:
            try:
                self.context.close()
            except Exception as e:
                logger.warning(f"Error closing browser context: {str(e)}")
        
        # Close browser
        if self.browser:
            try:
                self.browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {str(e)}")
        
        # Stop playwright
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {str(e)}")
        
        # Reset attributes
        self.playwright = None
        self.browser = None
        self.context = None
        
        logger.info("Browser stopped successfully") 