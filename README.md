# Localization3

A powerful tool for detecting localization issues in web applications using Amazon Nova Pro for OCR and language detection.

## Overview

Localization3 automates the process of:

1. Navigating through a web application
2. Capturing screenshots of pages and modals
3. Using Amazon Nova Pro for OCR and language detection
4. Flagging text that remains in English when the UI is set to French
5. Generating CSV and HTML reports of localization issues

## Features

- **Automated Navigation**: Traverses through ~60 pages and multiple modals
- **Screenshot Capture**: Takes high-quality screenshots of each page
- **OCR & Language Analysis**: Uses Amazon Nova Pro to extract text and detect languages
- **Localization Gap Detection**: Identifies English text that should be in French
- **Interactive Reports**: Generates both CSV and HTML reports with visual references
- **Manual Login Support**: Waits for user to manually log in before starting automated navigation

## Requirements

- Python 3.8 or later
- AWS account with access to Amazon Bedrock
- Access to Amazon Nova Pro model (must be requested in Amazon Bedrock console)
- Playwright installed for browser automation

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Gurgeron/Localization3.git
   cd Localization3
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

4. Copy `.env.template` to `.env` and fill in your AWS credentials:
   ```bash
   cp .env.template .env
   # Edit .env with your AWS credentials and configuration
   ```

## Configuration

- Edit `data/urls.txt` to specify which URLs to visit and capture
- Adjust settings in `.env` file as needed:
  - AWS credentials
  - AWS region
  - Amazon Nova model ID
  - Other configuration parameters

## Usage

### Basic Usage

```bash
python src/main.py --wait-for-login
```

This will:
1. Open a browser window
2. Wait for you to manually log in to the application
3. Once logged in, automatically navigate through the URLs specified in `data/urls.txt`
4. Capture screenshots of each page
5. Analyze the screenshots for localization issues
6. Generate reports in the `output/{timestamp}/reports` directory

### Command Line Options

- `--headless`: Run in headless mode (no visible browser window)
- `--output-dir PATH`: Specify the output directory (default: `output`)
- `--urls-file PATH`: Specify the file containing URLs to visit (default: `data/urls.txt`)
- `--wait-for-login`: Wait for manual login before starting navigation

## Understanding Reports

### CSV Report

The CSV report (`localization_issues.csv`) contains detailed information about each localization issue:
- Page ID
- URL
- Page title
- Text content
- Location in the UI
- Issue type
- Confidence level
- Screenshot reference

### HTML Report

The HTML report provides an interactive way to explore localization issues:
- Screenshot of each page
- Visual indicators of localization issues
- Ability to search and filter issues
- Full-size image viewing when clicking on screenshots

## AWS Cost Considerations

- The application uses Amazon Nova Pro through the Amazon Bedrock service, which has a usage-based cost
- Estimated cost is well under $50/month for typical usage
- Per-scan cost is minimal (<$0.10 per scan)

## Troubleshooting

### Common Issues

1. **AWS Authentication Errors**:
   - Check your AWS credentials in the `.env` file
   - Ensure you have requested and been granted access to the Amazon Nova Pro model

2. **Browser Automation Issues**:
   - Make sure Playwright is properly installed: `playwright install chromium`
   - Try updating Playwright: `pip install playwright --upgrade`

3. **Login Detection Problems**:
   - The tool tries to detect login completion automatically
   - If it fails to detect login, you may need to modify the detection logic in `page_navigator.py`

## Development

Want to contribute? Great!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Amazon Bedrock](https://aws.amazon.com/bedrock/) for providing the Nova Pro model
- [Playwright](https://playwright.dev/) for browser automation
- [Jinja2](https://jinja.palletsprojects.com/) for HTML template rendering 