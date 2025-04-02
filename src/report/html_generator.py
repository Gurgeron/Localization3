"""
HTML report generator module.
"""

import os
import logging
import json
from datetime import datetime
from pathlib import Path
import shutil
import jinja2

logger = logging.getLogger(__name__)

class HTMLReportGenerator:
    """
    A class for generating HTML reports of localization issues.
    
    This class handles creating HTML reports with details of localization issues,
    including screenshots and interactive elements.
    """
    
    def __init__(self, template_dir=None):
        """
        Initialize the HTML report generator.
        
        Args:
            template_dir (str): Path to the directory containing HTML templates.
                               If None, uses the default templates.
        """
        # Use default templates if none provided
        self.template_dir = template_dir or str(Path(__file__).parent / 'templates')
        
        # Set up the Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Create default template if it doesn't exist
        self._ensure_default_template()
    
    def _ensure_default_template(self):
        """Ensure that the default template exists, create if not."""
        template_dir = Path(self.template_dir)
        template_file = template_dir / 'report_template.html'
        
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
        
        if not template_file.exists():
            # Define the default HTML template
            default_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Localization Issues Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .page-section {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .page-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .page-title h2 {
            margin: 0;
            color: #2c3e50;
            font-size: 1.4em;
        }
        .issue-count {
            background-color: #e74c3c;
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .screenshot-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .screenshot:hover {
            transform: scale(1.01);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            padding: 20px;
            box-sizing: border-box;
        }
        .modal-content {
            display: block;
            margin: 0 auto;
            max-width: 90%;
            max-height: 90%;
        }
        .close {
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        .issues-list {
            list-style-type: none;
            padding: 0;
        }
        .issue-item {
            padding: 15px;
            border-left: 4px solid #e74c3c;
            background-color: #f9f9f9;
            margin-bottom: 10px;
            border-radius: 0 5px 5px 0;
        }
        .issue-text {
            font-weight: bold;
            color: #e74c3c;
        }
        .issue-location {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .issue-confidence {
            float: right;
            background-color: #3498db;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }
        .filter-controls {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .filter-controls input,
        .filter-controls select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .filter-controls button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        .filter-controls button:hover {
            background-color: #2980b9;
        }
        footer {
            text-align: center;
            margin-top: 50px;
            color: #7f8c8d;
        }
        @media (max-width: 768px) {
            .page-title {
                flex-direction: column;
                align-items: flex-start;
            }
            .issue-count {
                margin-top: 10px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Localization Issues Report</h1>
        <p>Generated on: {{ timestamp }}</p>
        <p>Total issues found: {{ issues|length }}</p>
    </header>

    <div class="summary">
        <h2>Summary</h2>
        <p>This report highlights UI elements that appear to be untranslated (remain in English when they should be in {{ target_language }}).</p>
        
        <div class="filter-controls">
            <input type="text" id="searchInput" placeholder="Search issues...">
            <select id="pageFilter">
                <option value="">All Pages</option>
                {% for page_id in pages %}
                <option value="{{ page_id }}">{{ page_id }}</option>
                {% endfor %}
            </select>
            <button id="resetFilters">Reset Filters</button>
        </div>
    </div>

    {% for page_id, page_data in grouped_issues.items() %}
    <div class="page-section" data-page-id="{{ page_id }}">
        <div class="page-title">
            <h2>{{ page_data.title }} ({{ page_id }})</h2>
            <div class="issue-count">{{ page_data.issues|length }}</div>
        </div>
        
        <div class="screenshot-container">
            <img src="{{ screenshots_dir }}/{{ page_id }}.png" alt="Screenshot of {{ page_id }}" class="screenshot" onclick="openModal('{{ screenshots_dir }}/{{ page_id }}.png')">
        </div>
        
        <h3>Issues Found:</h3>
        <ul class="issues-list">
            {% for issue in page_data.issues %}
            <li class="issue-item">
                <span class="issue-confidence">{{ (issue.confidence * 100)|int }}%</span>
                <div class="issue-text">{{ issue.text }}</div>
                <div class="issue-location">Location: {{ issue.location }}</div>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}

    <!-- Modal for enlarged screenshots -->
    <div id="screenshotModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>

    <footer>
        <p>Generated using Localization3 with Amazon Nova Pro</p>
    </footer>

    <script>
        // Modal functionality
        function openModal(imgSrc) {
            const modal = document.getElementById('screenshotModal');
            const modalImg = document.getElementById('modalImg');
            modal.style.display = 'block';
            modalImg.src = imgSrc;
        }
        
        function closeModal() {
            document.getElementById('screenshotModal').style.display = 'none';
        }

        // Search and filter functionality
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('searchInput');
            const pageFilter = document.getElementById('pageFilter');
            const resetButton = document.getElementById('resetFilters');
            const pageSections = document.querySelectorAll('.page-section');
            
            // Search functionality
            searchInput.addEventListener('input', filterContent);
            
            // Page filter
            pageFilter.addEventListener('change', filterContent);
            
            // Reset filters
            resetButton.addEventListener('click', function() {
                searchInput.value = '';
                pageFilter.value = '';
                filterContent();
            });
            
            function filterContent() {
                const searchTerm = searchInput.value.toLowerCase();
                const selectedPage = pageFilter.value;
                
                pageSections.forEach(section => {
                    const pageId = section.getAttribute('data-page-id');
                    const issueItems = section.querySelectorAll('.issue-item');
                    
                    // Check if page matches filter
                    const pageMatch = !selectedPage || pageId === selectedPage;
                    
                    if (!pageMatch) {
                        section.style.display = 'none';
                        return;
                    }
                    
                    // Check if any issues match search term
                    let hasMatchingIssue = false;
                    
                    issueItems.forEach(item => {
                        const issueText = item.querySelector('.issue-text').textContent.toLowerCase();
                        const issueLocation = item.querySelector('.issue-location').textContent.toLowerCase();
                        
                        const matches = !searchTerm || 
                                       issueText.includes(searchTerm) || 
                                       issueLocation.includes(searchTerm);
                        
                        item.style.display = matches ? 'block' : 'none';
                        
                        if (matches) {
                            hasMatchingIssue = true;
                        }
                    });
                    
                    section.style.display = hasMatchingIssue ? 'block' : 'none';
                });
            }
        });
    </script>
</body>
</html>
"""
            # Save the default template
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(default_template)
    
    def generate_report(self, results, output_path, screenshots_dir=None, target_language='French'):
        """
        Generate an HTML report of localization issues.
        
        Args:
            results (list): List of dictionaries containing issue details.
            output_path (str): Path to save the HTML file.
            screenshots_dir (str): Path to the directory containing screenshots.
            target_language (str): The target language for localization.
            
        Returns:
            bool: True if the report was generated successfully, False otherwise.
        """
        logger.info(f"Generating HTML report at: {output_path}")
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Group issues by page
            grouped_issues = {}
            unique_pages = set()
            
            for result in results:
                page_id = result.get('page_id', 'unknown')
                unique_pages.add(page_id)
                
                if page_id not in grouped_issues:
                    grouped_issues[page_id] = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'issues': []
                    }
                
                grouped_issues[page_id]['issues'].append({
                    'text': result.get('text', ''),
                    'location': result.get('location', 'Unknown'),
                    'confidence': result.get('confidence', 1.0),
                    'issue_type': result.get('issue_type', 'Missing Translation')
                })
            
            # Get relative path to screenshots (for HTML)
            rel_screenshots_dir = screenshots_dir
            if screenshots_dir:
                # Try to make the path relative to the HTML file
                output_dir = os.path.dirname(output_path)
                try:
                    rel_screenshots_dir = os.path.relpath(screenshots_dir, output_dir)
                except ValueError:
                    # If paths are on different drives, keep the original path
                    pass
            
            # Prepare template data
            template_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'issues': results,
                'grouped_issues': grouped_issues,
                'pages': sorted(list(unique_pages)),
                'screenshots_dir': rel_screenshots_dir or 'screenshots',
                'target_language': target_language
            }
            
            # Load and render the template
            template = self.jinja_env.get_template('report_template.html')
            rendered_html = template.render(**template_data)
            
            # Write the HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            # Copy screenshots to report directory if needed
            if screenshots_dir and os.path.exists(screenshots_dir):
                report_screenshots_dir = os.path.join(os.path.dirname(output_path), 'screenshots')
                if screenshots_dir != report_screenshots_dir and not os.path.samefile(screenshots_dir, report_screenshots_dir):
                    if not os.path.exists(report_screenshots_dir):
                        os.makedirs(report_screenshots_dir, exist_ok=True)
                    
                    # Copy only screenshots that are referenced in the report
                    for page_id in unique_pages:
                        src_file = os.path.join(screenshots_dir, f"{page_id}.png")
                        if os.path.exists(src_file):
                            shutil.copy2(src_file, report_screenshots_dir)
            
            # Log success
            logger.info(f"HTML report generated successfully with {len(unique_pages)} pages and {len(results)} issues")
            return True
        
        except Exception as e:
            logger.exception(f"Error generating HTML report: {str(e)}")
            return False 