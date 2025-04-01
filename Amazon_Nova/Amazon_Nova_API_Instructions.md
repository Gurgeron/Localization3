# Amazon Nova API - Step-by-Step Instructions

## Introduction

This document provides practical step-by-step instructions for using Amazon Nova models through the Amazon Bedrock API. These instructions focus on practical implementation for developers.

## Prerequisites

1. An AWS account with Amazon Bedrock permissions
2. Access to Amazon Nova models (must be requested in Amazon Bedrock console)
3. AWS credentials configured for programmatic access
4. Basic knowledge of AWS SDK in your preferred programming language

## Setup Process

### 1. Install Required Dependencies

#### Python Example
```python
# Install the AWS SDK for Python
pip install boto3
```

#### JavaScript Example
```javascript
// Install the AWS SDK for JavaScript
npm install @aws-sdk/client-bedrock-runtime
```

### 2. Configure AWS Credentials

#### Using AWS CLI
```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and Region
```

#### Programmatically
```python
# Python example
import boto3
session = boto3.Session(
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-east-1'  # Primary region for Nova models
)
```

### 3. Request Model Access

You must request access to Amazon Nova models through the Amazon Bedrock console before using them via API:

1. Visit https://console.aws.amazon.com/bedrock/
2. Navigate to "Model access" under Bedrock configurations
3. Choose "Enable specific models"
4. Select the Amazon Nova models you need
5. Submit your request

## Using the API

### Method 1: Converse API (Recommended for Chat Applications)

The Converse API is ideal for chat applications and provides a simpler interface for managing conversations.

#### Python Example
```python
import boto3
import json

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Example conversation with Amazon Nova Lite
response = bedrock_runtime.converse(
    modelId='amazon.nova-lite-v1:0',
    messages=[
        {
            'role': 'user',
            'content': [
                {
                    'text': 'What are the benefits of cloud computing?'
                }
            ]
        }
    ]
)

# Parse and print the response
for message in response['messages']:
    if message['role'] == 'assistant':
        for content in message['content']:
            if 'text' in content:
                print(content['text'])
```

### Method 2: InvokeModel API

The InvokeModel API provides more direct control over model invocation.

#### Python Example
```python
import boto3
import json

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Example request payload for Amazon Nova Lite
request_payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
        {
            "role": "user",
            "content": "What are the benefits of cloud computing?"
        }
    ]
}

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId='amazon.nova-lite-v1:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps(request_payload)
)

# Parse and print the response
response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
```

## Working with Multimodal Content

### Image Understanding

#### Python Example
```python
import boto3
import json
import base64

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Read and encode an image
with open('image.jpg', 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# Create the request payload
request_payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
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
                    "text": "Describe what's in this image in detail."
                }
            ]
        }
    ]
}

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId='amazon.nova-pro-v1:0',  # Using Nova Pro for image understanding
    contentType='application/json',
    accept='application/json',
    body=json.dumps(request_payload)
)

# Parse and print the response
response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
```

### Image Generation

#### Python Example
```python
import boto3
import json
import base64
import os

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Create the request payload for image generation
request_payload = {
    "taskType": "TEXT_IMAGE",
    "textToImageParams": {
        "text": "A serene lake surrounded by mountains at sunset",
        "negativeText": "blurry, distorted, low quality"
    },
    "imageGenerationConfig": {
        "numberOfImages": 1,
        "height": 1024,
        "width": 1024,
        "cfgScale": 8.0
    }
}

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId='amazon.nova-canvas-v1:0',  # Using Nova Canvas for image generation
    contentType='application/json',
    accept='application/json',
    body=json.dumps(request_payload)
)

# Parse the response and save the generated image
response_body = json.loads(response['body'].read())
for i, image in enumerate(response_body['images']):
    image_data = base64.b64decode(image)
    with open(f'generated_image_{i}.png', 'wb') as f:
        f.write(image_data)
    print(f"Image saved as generated_image_{i}.png")
```

## Using System Prompts

System prompts help define the role and behavior of the model:

```python
import boto3
import json

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Example with system prompt
request_payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "system": "You are a friendly assistant that specializes in explaining complex technical concepts in simple terms.",
    "messages": [
        {
            "role": "user",
            "content": "Explain how cloud computing works."
        }
    ]
}

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId='amazon.nova-lite-v1:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps(request_payload)
)

# Parse and print the response
response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
```

## Tool Usage Example

Amazon Nova models support tool usage for extending their capabilities:

```python
import boto3
import json

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Define tools
tools = [
    {
        "name": "weather",
        "description": "Get current weather for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        }
    }
]

# Example with tool definition
request_payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "tools": tools,
    "messages": [
        {
            "role": "user",
            "content": "What's the weather like in Seattle right now?"
        }
    ]
}

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId='amazon.nova-pro-v1:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps(request_payload)
)

# Parse the response to see tool calls
response_body = json.loads(response['body'].read())
print(json.dumps(response_body, indent=2))

# If tool calls were made, you would process them here
# and then call the model again with the tool results
```

## Best Practices

1. **Request Structure**
   - Include only necessary parameters
   - Use appropriate model for the task (Pro, Lite, or Micro)
   - Set reasonable max_tokens values

2. **Error Handling**
   - Implement robust error handling for API calls
   - Handle rate limiting and quota exceptions
   - Consider implementing retries with exponential backoff

3. **Performance Optimization**
   - Cache responses where appropriate
   - Use streaming for better user experience with longer responses
   - Consider batch processing for non-interactive applications

4. **Security**
   - Never expose AWS credentials in client-side code
   - Implement proper IAM policies and permissions
   - Validate and sanitize all user inputs

## Troubleshooting

1. **Access Issues**
   - Ensure you've requested and been granted access to the models
   - Verify your IAM permissions include bedrock:InvokeModel

2. **Quota Limits**
   - Check your service quotas in the AWS console
   - Request quota increases if needed

3. **Error Responses**
   - 400 errors: Check request format and model availability
   - 429 errors: You're being throttled, implement backoff strategy
   - 500 errors: Service issue, retry with backoff

## Changelog

- Initial creation of API instructions

## Notes

This guide provides practical examples for getting started with Amazon Nova through the Bedrock API. For complete API documentation, refer to the official Amazon Bedrock API Reference. 