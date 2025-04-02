#!/usr/bin/env python3
"""
Localization3 - Tool for detecting localization issues in web applications

This tool automates the process of:
1. Navigating through a web application
2. Capturing screenshots of pages and modals
3. Using Amazon Nova Pro for OCR and language detection
4. Flagging text that remains in English when the UI is set to French
5. Generating a CSV and HTML report of localization issues
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import internal modules
from navigator.browser import Browser
from navigator.page_navigator import PageNavigator
from ocr.amazon_nova import NovaImageAnalyzer
from report.csv_generator import CSVReportGenerator
from report.html_generator import HTMLReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('localization3.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Localization3 - Tool for detecting localization issues')
    
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to store screenshots and reports')
    parser.add_argument('--urls-file', type=str, default='data/urls.txt',
                        help='File containing URLs to visit')
    parser.add_argument('--wait-for-login', action='store_true',
                        help='Wait for manual login before starting navigation')
    
    return parser.parse_args()

def setup_directories(base_dir):
    """Create necessary directories for output."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(base_dir) / timestamp
    
    # Create directories
    screenshots_dir = output_dir / 'screenshots'
    reports_dir = output_dir / 'reports'
    
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        'output': output_dir,
        'screenshots': screenshots_dir,
        'reports': reports_dir
    }

def load_urls(urls_file):
    """Load URLs to visit from a file."""
    try:
        with open(urls_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        logger.error(f"URLs file not found: {urls_file}")
        return []

def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup directories
    dirs = setup_directories(args.output_dir)
    logger.info(f"Output directory: {dirs['output']}")
    
    # Load URLs to visit
    urls = load_urls(args.urls_file)
    if not urls:
        logger.error("No URLs to visit. Exiting.")
        return 1
    
    # Initialize components
    try:
        browser = Browser(headless=args.headless)
        navigator = PageNavigator(browser)
        analyzer = NovaImageAnalyzer()
        
        # Start browser
        page = browser.start()
        
        # Handle manual login if required
        if args.wait_for_login:
            logger.info("Please log in manually to the application.")
            navigator.wait_for_login_completion(page)
            logger.info("Login detected. Proceeding with navigation.")
        
        # Process each URL
        results = []
        for url in urls:
            logger.info(f"Processing URL: {url}")
            
            # Navigate to the URL
            page_info = navigator.navigate_to_url(page, url)
            
            # Capture screenshot
            screenshot_path = dirs['screenshots'] / f"{page_info['id']}.png"
            navigator.capture_screenshot(page, str(screenshot_path))
            
            # Analyze screenshot with Amazon Nova
            analysis_result = analyzer.analyze_image(
                image_path=str(screenshot_path),
                target_language="French"
            )
            
            # Add results to the list
            if analysis_result['issues']:
                for issue in analysis_result['issues']:
                    results.append({
                        'page_id': page_info['id'],
                        'url': url,
                        'title': page_info['title'],
                        'text': issue['text'],
                        'issue_type': issue['type'],
                        'screenshot': str(screenshot_path)
                    })
        
        # Generate reports
        csv_path = dirs['reports'] / 'localization_issues.csv'
        html_path = dirs['reports'] / 'localization_issues.html'
        
        csv_generator = CSVReportGenerator()
        csv_generator.generate_report(results, str(csv_path))
        
        html_generator = HTMLReportGenerator()
        html_generator.generate_report(results, str(html_path), str(dirs['screenshots']))
        
        logger.info(f"CSV report generated: {csv_path}")
        logger.info(f"HTML report generated: {html_path}")
        
        # Close browser
        browser.stop()
        
        return 0
    
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 