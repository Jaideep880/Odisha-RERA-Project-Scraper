# Odisha RERA Project Data Extractor

A Python script that extracts project information from the Odisha RERA website and saves it in a structured format.

## Overview

This script automates the process of collecting project details from the Odisha RERA website. It extracts the following information for the first 6 registered projects:
- RERA Registration Number
- Project Name
- Promoter Details (Company Name)
- Registered Office Address
- GST Number

## Prerequisites

- Python 3.x
- Google Chrome browser
- Internet connection

## Setup

1. Install Python from [python.org](https://python.org)

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python rera_scraper.py
```

The script will:
- Access the Odisha RERA website
- Extract project details
- Save the data to 'odisha_rera_projects.csv'

## Output Format

The script generates a CSV file with the following columns:
- RERA Regd. No
- Project Name
- Promoter Name
- Promoter Address
- GST No

## Technical Details

- Uses Selenium WebDriver for browser automation
- Implements error handling for missing data
- Runs in headless mode for efficiency 