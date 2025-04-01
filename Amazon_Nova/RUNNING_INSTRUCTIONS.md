# Running Amazon Nova with Amazon Bedrock SDK

This document provides detailed instructions on how to set up and run code that uses Amazon Nova models through the Amazon Bedrock SDK.

## Installation Requirements

### Prerequisites

- Python 3.8 or later
- An AWS account with access to Amazon Bedrock
- Amazon Nova models access (must be requested in the Amazon Bedrock console)

### Setting Up Your Development Environment

1. **Create a virtual environment** (recommended)

   ```bash
   # Create a virtual environment
   python -m venv nova-env
   
   # Activate the virtual environment
   # On Windows:
   nova-env\Scripts\activate
   # On macOS/Linux:
   source nova-env/bin/activate
   ```

2. **Install required packages**

   ```bash
   pip install boto3 python-dotenv
   ```

3. **Configure AWS credentials**

   Follow the instructions in [API_KEYS_CONFIG.md](API_KEYS_CONFIG.md) to set up your AWS credentials.

## Running Example Code

### 1. Basic Text Generation Example

Create a file named `text_generation.py` with the following content:

```python
import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_text(prompt):
    """Generate text using Amazon Nova Lite"""
    
    # Initialize the Bedrock Runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # Create the request payload
    request_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": int(os.getenv('MAX_TOKENS', 1000)),
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # Invoke the model
    try:
        response = bedrock_runtime.invoke_model(
            modelId=os.getenv('NOVA_MODEL_ID', 'amazon.nova-lite-v1:0'),
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_payload)
        )
        
        # Parse and return the response
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

if __name__ == "__main__":
    user_prompt = input("Enter your prompt: ")
    response = generate_text(user_prompt)
    if response:
        print("\nGenerated Response:")
        print(response)
```

Run the example:

```bash
python text_generation.py
```

### 2. Image Understanding Example

Create a file named `image_understanding.py` with the following content:

```python
import boto3
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_image(image_path, prompt):
    """Analyze an image using Amazon Nova Pro"""
    
    # Initialize the Bedrock Runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # Read and encode the image
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None
    
    # Create the request payload
    request_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": int(os.getenv('MAX_TOKENS', 1000)),
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
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    # Invoke the model
    try:
        response = bedrock_runtime.invoke_model(
            modelId='amazon.nova-pro-v1:0',  # Using Nova Pro for image understanding
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_payload)
        )
        
        # Parse and return the response
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None

if __name__ == "__main__":
    image_path = input("Enter the path to your image file: ")
    user_prompt = input("Enter your question about the image: ")
    
    response = analyze_image(image_path, user_prompt)
    if response:
        print("\nAnalysis Result:")
        print(response)
```

Run the example:

```bash
python image_understanding.py
```

### 3. Image Generation Example

Create a file named `image_generation.py` with the following content:

```python
import boto3
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_image(prompt, negative_prompt=""):
    """Generate an image using Amazon Nova Canvas"""
    
    # Initialize the Bedrock Runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # Create the request payload
    request_payload = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt,
            "negativeText": negative_prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 1024,
            "width": 1024,
            "cfgScale": 8.0
        }
    }
    
    # Invoke the model
    try:
        response = bedrock_runtime.invoke_model(
            modelId='amazon.nova-canvas-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_payload)
        )
        
        # Parse and save the response
        response_body = json.loads(response['body'].read())
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        image_paths = []
        for i, image in enumerate(response_body['images']):
            image_data = base64.b64decode(image)
            image_path = f"{output_dir}/generated_image_{i}.png"
            with open(image_path, 'wb') as f:
                f.write(image_data)
            image_paths.append(image_path)
            
        return image_paths
    
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

if __name__ == "__main__":
    prompt = input("Enter your image prompt: ")
    negative_prompt = input("Enter negative prompt (optional, press Enter to skip): ")
    
    image_paths = generate_image(prompt, negative_prompt)
    if image_paths:
        print("\nGenerated images saved at:")
        for path in image_paths:
            print(path)
```

Run the example:

```bash
python image_generation.py
```

## Troubleshooting Common Issues

### 1. Authentication Issues

**Problem**: `botocore.exceptions.ClientError: An error occurred (AccessDeniedException) when calling the InvokeModel operation`

**Solution**:
- Verify your AWS credentials are correctly set up
- Check that your IAM user/role has the `bedrock:InvokeModel` permission
- Confirm you've requested and been granted access to the Nova models

### 2. Model Access Issues

**Problem**: `botocore.exceptions.ClientError: An error occurred (ModelNotReadyException)`

**Solution**:
- Request access to the model in the Amazon Bedrock console
- Verify that access has been granted
- Make sure you're using the correct region where access was granted

### 3. Rate Limiting

**Problem**: `botocore.exceptions.ClientError: An error occurred (ThrottlingException)`

**Solution**:
- Implement exponential backoff and retry logic
- Request higher quota limits if needed for your application
- Optimize your application to make fewer API calls

### 4. Image Processing Issues

**Problem**: Image upload fails or gives unexpected results

**Solution**:
- Check that your image is in a supported format (JPEG, PNG, etc.)
- Verify the image size is within limits (less than 20MB)
- Ensure the base64 encoding is correct

## Advanced Configuration

For advanced use cases, you may want to create a configuration file that allows for more detailed settings. Create a file named `config.json` with the following structure:

```json
{
  "models": {
    "text": "amazon.nova-lite-v1:0",
    "multimodal": "amazon.nova-pro-v1:0",
    "image_generation": "amazon.nova-canvas-v1:0"
  },
  "parameters": {
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9
  },
  "image_config": {
    "width": 1024,
    "height": 1024,
    "number_of_images": 1,
    "cfg_scale": 8.0
  }
}
```

You can then load this configuration in your Python scripts:

```python
import json

def load_config(config_path="config.json"):
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()
```

## Additional Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS SDK Examples for Amazon Bedrock](https://github.com/aws-samples/amazon-bedrock-samples)

## Changelog

- Initial creation of running instructions 