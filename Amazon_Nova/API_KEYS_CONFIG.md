# Amazon Nova API Keys Configuration

This file provides guidance on how to securely manage your API keys and configurations for Amazon Nova.

## AWS Credentials

Your AWS credentials should be stored securely and never committed to version control. There are several methods to manage your credentials:

### 1. AWS CLI Configuration

Use the AWS CLI to configure your credentials locally:

```bash
aws configure
```

This will prompt you to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (use `us-east-1` for primary Amazon Nova access)
- Default output format (recommended: `json`)

This creates a file at `~/.aws/credentials` that AWS SDKs can automatically use.

### 2. Environment Variables

Set environment variables in your development environment:

```bash
# Linux/Mac
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### 3. AWS IAM Roles

For production applications running on AWS services like EC2, Lambda, or ECS, use IAM roles instead of hard-coded credentials. This is the most secure approach.

## Amazon Bedrock Configuration

### Model IDs

Use these model IDs when making API calls:

- **Amazon Nova Pro**: `amazon.nova-pro-v1:0`
- **Amazon Nova Lite**: `amazon.nova-lite-v1:0`
- **Amazon Nova Micro**: `amazon.nova-micro-v1:0`
- **Amazon Nova Canvas**: `amazon.nova-canvas-v1:0`
- **Amazon Nova Reel**: `amazon.nova-reel-v1:0`

### Recommended Regions

Primary regions for Amazon Nova models:
- US East (N. Virginia) - `us-east-1` (Recommended)
- Asia Pacific (Tokyo) - `ap-northeast-1`

Cross-region inference is available from additional regions.

## Security Best Practices

1. **Never hardcode API keys in application code**
2. **Rotate credentials regularly**
3. **Use IAM roles with least privilege**
4. **Enable AWS CloudTrail** to monitor API usage
5. **Consider using AWS Secrets Manager** for production deployments

## Environment-Specific Configuration Template

Create a `.env` file for your project (and add it to `.gitignore`):

```
# AWS Credentials - DO NOT COMMIT THIS FILE TO VERSION CONTROL
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Amazon Bedrock Configuration
NOVA_MODEL_ID=amazon.nova-lite-v1:0
MAX_TOKENS=1000
TEMPERATURE=0.7
```

## Loading Environment Variables in Different Languages

### Python (using python-dotenv)
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
```

### JavaScript/Node.js (using dotenv)
```javascript
require('dotenv').config();

const awsAccessKey = process.env.AWS_ACCESS_KEY_ID;
const awsSecretKey = process.env.AWS_SECRET_ACCESS_KEY;
const awsRegion = process.env.AWS_REGION;
```

## Production Deployment Recommendations

For production environments:

1. **Use AWS Secrets Manager** to store and retrieve credentials
2. **Implement proper error handling** for credential access
3. **Set up alerts** for unauthorized API access attempts
4. **Use different credentials** for development, staging, and production environments
5. **Consider using AWS Parameter Store** for configuration values

## Important Note

⚠️ This file should be used as a template and should NOT contain actual API keys. Replace placeholder values with your actual credentials only in your local, secure environment. 