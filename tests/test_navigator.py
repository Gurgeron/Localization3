"""
Tests for the navigator module.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from src.navigator.browser import Browser
from src.navigator.page_navigator import PageNavigator

@pytest.fixture
def mock_browser():
    """Create a mock browser for testing."""
    browser = MagicMock()
    browser.start.return_value = MagicMock()
    return browser

@pytest.fixture
def navigator(mock_browser):
    """Create a navigator instance with a mock browser."""
    return PageNavigator(mock_browser)

def test_browser_initialization():
    """Test browser initialization with default parameters."""
    with patch('src.navigator.browser.sync_playwright') as mock_playwright:
        browser = Browser(headless=True)
        assert browser.headless is True
        assert browser.browser_type == 'chromium'
        assert browser.viewport_size == {'width': 1280, 'height': 800}

def test_generate_page_id():
    """Test page ID generation from URL and title."""
    navigator = PageNavigator(MagicMock())
    
    # Test with simple homepage
    page_id = navigator._generate_page_id('https://example.com/', 'Example Site')
    assert page_id == 'home_example_site'
    
    # Test with path
    page_id = navigator._generate_page_id('https://example.com/products', 'Products')
    assert page_id == 'products_products'
    
    # Test with nested path
    page_id = navigator._generate_page_id('https://example.com/products/category/item', 'Item Details')
    assert page_id == 'products_category_item_item_details'
    
    # Test with query parameters
    page_id = navigator._generate_page_id('https://example.com/search?q=test', 'Search Results')
    assert 'search_search_results_q' in page_id

def test_capture_screenshot(navigator, tmp_path):
    """Test screenshot capture functionality."""
    # Mock the page
    mock_page = MagicMock()
    
    # Create a temporary file path for the screenshot
    screenshot_path = os.path.join(tmp_path, 'test_screenshot.png')
    
    # Test the capture_screenshot method
    with patch('os.makedirs') as mock_makedirs:
        result = navigator.capture_screenshot(mock_page, screenshot_path)
        
        # Verify the method returns True
        assert result is True
        
        # Verify the screenshot method was called with the correct path
        mock_page.screenshot.assert_called_once_with(path=screenshot_path, full_page=True)
        
        # Verify the directory was created
        mock_makedirs.assert_called_once() 