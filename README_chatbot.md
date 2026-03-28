# Data Analyst Chatbot CLI

This script allows you to query datasets using natural language. It generates pandas code via Gemini and executes it safely.

## Setup

Activate virtual environment:
source venv/bin/activate  (Linux/Mac)
venv\Scripts\activate   (Windows)

Install dependencies:
pip install pandas google-genai python-dotenv

Create .env file:
GEMINI_API_KEY=your_api_key_here

## Run
python src/chatbot/main.py

## Usage
df_input: your question
df_orders: your question

Example:
df_orders: average orders by city

Type 'endchat' to exit.
