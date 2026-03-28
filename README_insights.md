# Insight Detection & Executive Report Generator

This script processes datasets, detects insights, and generates a PDF report.

## Setup

Activate virtual environment:
source venv/bin/activate  (Linux/Mac)
venv\Scripts\activate   (Windows)

Install dependencies:
pip install pandas numpy google-genai python-dotenv reportlab

Create .env file:
GEMINI_API_KEY=your_api_key_here

## Run
python src/insights/main.py

## Output
reports/output/executive_report.pdf

## Notes
- Requires CSV files in data/processed/
- Ensure executive_report_gen.py exists
