"""
Amazon Nova integration module for OCR and language detection.
"""

import os
import base64
import json
import logging
import boto3
from botocore.exceptions import ClientError
from PIL import Image

logger = logging.getLogger(__name__)

class NovaImageAnalyzer:
    """
    A class for analyzing images using Amazon Nova Pro.
    
    This class handles sending images to Amazon Nova Pro for OCR and
    language detection, and processing the results to identify localization issues.
    """
    
    def __init__(self, region_name=None, max_tokens=4000):
        """
        Initialize the Amazon Nova analyzer.
        
        Args:
            region_name (str): AWS region name. If None, uses the value from
                              AWS_REGION environment variable or 'us-east-1' as fallback.
            max_tokens (int): Maximum token limit for the model response.
        """
        self.region_name = region_name or os.environ.get('AWS_REGION', 'us-east-1')
        self.max_tokens = max_tokens
        self.model_id = os.environ.get('NOVA_PRO_MODEL_ID', 'amazon.nova-pro-v1:0')
        
        # Initialize the Bedrock Runtime client
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.region_name
        )
    
    def analyze_image(self, image_path, target_language='French'):
        """
        Analyze an image for localization issues.
        
        This method sends an image to Amazon Nova Pro, extracts text,
        detects the language, and identifies content that should be
        translated but remains in English.
        
        Args:
            image_path (str): Path to the image file.
            target_language (str): The expected language for UI elements.
            
        Returns:
            dict: Analysis results including detected issues.
        """
        logger.info(f"Analyzing image: {image_path}")
        
        try:
            # Read and encode the image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Get image dimensions for reference
            with Image.open(image_path) as img:
                image_width, image_height = img.size
            
            # Create the system prompt for localization analysis
            system_prompt = f"""
            You are a localization expert tasked with identifying text in a UI screenshot that should be translated
            to {target_language} but remains in English. Your task is to:
            
            1. Identify all text elements in the UI
            2. Determine the language of each text element
            3. Flag any text that is in English but should be in {target_language}
            
            Ignore:
            - User-generated content
            - Names, emails, or personal identifiers
            - Proper nouns or brand names
            - Technical terms that are conventionally kept in English
            
            Provide your analysis in a structured JSON format with these fields:
            - text: The exact text content
            - language: The detected language
            - should_be_translated: Boolean indicating if this should be translated
            - confidence: Your confidence level (0-1) that this is a localization issue
            - location: General location description in the UI
            """
            
            # Create the user prompt
            user_prompt = "Find all English text in this UI screenshot that should be localized to French."
            
            # Create the request payload
            request_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": user_prompt
                            }
                        ]
                    }
                ]
            }
            
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_payload)
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Extract the JSON part of the response
            try:
                # Find JSON content in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = response_text[json_start:json_end]
                    issues_data = json.loads(json_content)
                else:
                    # Try to extract an array if no object is found
                    json_start = response_text.find('[')
                    json_end = response_text.rfind(']') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_content = response_text[json_start:json_end]
                        issues_data = json.loads(json_content)
                    else:
                        logger.warning("No JSON content found in response")
                        issues_data = []
                
                # Normalize the response format
                if isinstance(issues_data, dict) and 'issues' in issues_data:
                    localization_issues = issues_data['issues']
                elif isinstance(issues_data, dict) and 'elements' in issues_data:
                    localization_issues = issues_data['elements']
                elif isinstance(issues_data, list):
                    localization_issues = issues_data
                else:
                    localization_issues = []
                
                # Filter for actual issues
                filtered_issues = []
                for issue in localization_issues:
                    if issue.get('should_be_translated', False) and issue.get('language', '').lower() == 'english':
                        filtered_issues.append({
                            'text': issue.get('text', ''),
                            'location': issue.get('location', 'Unknown'),
                            'confidence': issue.get('confidence', 1.0),
                            'type': 'Missing Translation'
                        })
                
                logger.info(f"Found {len(filtered_issues)} localization issues")
                
                return {
                    'image_path': image_path,
                    'image_dimensions': {'width': image_width, 'height': image_height},
                    'target_language': target_language,
                    'issues': filtered_issues
                }
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON in Nova response: {str(e)}")
                logger.debug(f"Response text: {response_text}")
                return {
                    'image_path': image_path,
                    'issues': []
                }
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"AWS Bedrock error ({error_code}): {error_message}")
            return {
                'image_path': image_path,
                'error': f"AWS Bedrock error: {error_message}",
                'issues': []
            }
        
        except Exception as e:
            logger.exception(f"Error analyzing image: {str(e)}")
            return {
                'image_path': image_path,
                'error': f"Analysis error: {str(e)}",
                'issues': []
            } 