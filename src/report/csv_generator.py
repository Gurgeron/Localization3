"""
CSV report generator module.
"""

import csv
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class CSVReportGenerator:
    """
    A class for generating CSV reports of localization issues.
    
    This class handles creating CSV files with details of localization issues found
    during the analysis process.
    """
    
    def __init__(self):
        """Initialize the CSV report generator."""
        pass
    
    def generate_report(self, results, output_path):
        """
        Generate a CSV report of localization issues.
        
        Args:
            results (list): List of dictionaries containing issue details.
            output_path (str): Path to save the CSV file.
            
        Returns:
            bool: True if the report was generated successfully, False otherwise.
        """
        logger.info(f"Generating CSV report at: {output_path}")
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Define CSV columns
            fieldnames = [
                'page_id',
                'url',
                'title',
                'text',
                'location',
                'issue_type',
                'confidence',
                'screenshot'
            ]
            
            # Write the CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    # Write row for each issue
                    writer.writerow({
                        'page_id': result.get('page_id', ''),
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'text': result.get('text', ''),
                        'location': result.get('location', ''),
                        'issue_type': result.get('issue_type', 'Missing Translation'),
                        'confidence': result.get('confidence', 1.0),
                        'screenshot': result.get('screenshot', '')
                    })
            
            # Log success
            logger.info(f"CSV report generated successfully with {len(results)} issues")
            return True
        
        except Exception as e:
            logger.exception(f"Error generating CSV report: {str(e)}")
            return False
    
    def generate_summary_report(self, results, output_path):
        """
        Generate a summary CSV report with aggregated statistics.
        
        Args:
            results (list): List of dictionaries containing issue details.
            output_path (str): Path to save the summary CSV file.
            
        Returns:
            bool: True if the summary report was generated successfully, False otherwise.
        """
        logger.info(f"Generating summary CSV report at: {output_path}")
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Aggregate results by page
            page_stats = {}
            for result in results:
                page_id = result.get('page_id', 'unknown')
                url = result.get('url', '')
                title = result.get('title', '')
                
                if page_id not in page_stats:
                    page_stats[page_id] = {
                        'page_id': page_id,
                        'url': url,
                        'title': title,
                        'issue_count': 0,
                        'screenshot': result.get('screenshot', '')
                    }
                
                page_stats[page_id]['issue_count'] += 1
            
            # Define CSV columns for summary
            fieldnames = [
                'page_id',
                'url',
                'title',
                'issue_count',
                'screenshot'
            ]
            
            # Write the summary CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Sort pages by issue count (descending)
                sorted_pages = sorted(
                    page_stats.values(),
                    key=lambda x: x['issue_count'],
                    reverse=True
                )
                
                for page in sorted_pages:
                    writer.writerow(page)
            
            # Log success
            logger.info(f"Summary report generated with {len(page_stats)} pages")
            return True
        
        except Exception as e:
            logger.exception(f"Error generating summary report: {str(e)}")
            return False 