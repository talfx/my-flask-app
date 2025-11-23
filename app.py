from flask import Flask, request, jsonify
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def data_prep(data):
    """
    Prepare and clean feedback data
    - Convert JSON to pandas DataFrame
    - Keep only 'name' and 'feedback' fields
    - Remove duplicates, nulls, and invalid entries
    - Return cleaned data as list of dicts
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Keep only necessary columns
        if 'name' not in df.columns or 'feedback' not in df.columns:
            raise ValueError("Missing 'name' or 'feedback' columns")
        
        df = df[['name', 'feedback']]
        
        # Remove nulls and empty strings
        df = df.dropna()
        df = df[df['feedback'].str.strip() != '']
        df = df[df['name'].str.strip() != '']
        
        # Remove duplicates (keep first occurrence)
        df = df.drop_duplicates(subset=['feedback'], keep='first')
        
        # Ensure feedback is string type
        df['feedback'] = df['feedback'].astype(str)
        df['name'] = df['name'].astype(str)
        
        print(f"Data prepared: {len(df)} valid entries")
        
        # Convert back to list of dicts
        return df.to_dict('records')
    
    except Exception as e:
        print(f"Error in data_prep: {str(e)}")
        raise


def analyze_with_openai(data):
    """
    Call OpenAI API to analyze feedback
    - Summarize key themes
    - Identify top positive and negative points
    - Suggest 1 improvement idea
    - Classify sentiment for each feedback
    """
    try:
        # Format feedback for OpenAI
        formatted_feedback = "\n".join([
            f"- {item.get('name', 'Anonymous')}: {item.get('feedback', '')}"
            for item in data
        ])
        
        # Create detailed prompt
        prompt = f"""Analyze the following customer feedback and provide:

1. A brief summary of key themes (2-3 sentences)
2. Top 3 positive points (if any exist)
3. Top 3 negative points (if any exist)
4. One specific, actionable improvement suggestion
5. Sentiment classification for each piece of feedback (Positive/Negative/Neutral)

Format your response as JSON with these exact keys:
- summary: brief overall summary
- positive_points: list of top positive points
- negative_points: list of top negative points
- improvement_suggestion: one actionable improvement
- sentiment_breakdown: list with name and sentiment for each feedback (format: "Name: Sentiment")
- total_feedback_analyzed: number of feedback entries

Customer Feedback:
{formatted_feedback}"""
        
        print("Calling OpenAI API...")
        
        # Call OpenAI API
        message = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract response
        response_text = message.choices[0].message.content
        print(f"OpenAI response: {response_text[:200]}...")
        
        # Try to parse as JSON
        try:
            import json
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # If OpenAI didn't return pure JSON, wrap the response
            analysis = {
                "summary": response_text,
                "raw_response": response_text
            }
        
        # Create response object
        result = {
            "length": len(data),
            "response_date": datetime.now().isoformat(),
            "analysis": analysis
        }
        
        return result
    
    except Exception as e:
        print(f"Error in analyze_with_openai: {str(e)}")
        raise


@app.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    print("=" * 50)
    print("DATA RECEIVED:")
    try:
        data = request.json
        print(f"Raw data: {data}")
        
        # Extract just the feedback items from n8n's format
        if isinstance(data, list):
            feedback_list = [item.get('json', item) for item in data]
        else:
            feedback_list = data
        
        print(f"Extracted feedback_list: {len(feedback_list)} items")
        
        # Prepare/clean data
        cleaned_data = data_prep(feedback_list)
        
        # Call OpenAI for analysis
        openai_response = analyze_with_openai(cleaned_data)
        
        return jsonify({
            "status": "success",
            "feedback_count": len(cleaned_data),
            "data": openai_response
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "Feedback Analyzer"}), 200


@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API documentation"""
    return jsonify({
        "service": "AI-Powered Feedback Analyzer",
        "version": "2.0",
        "endpoints": {
            "/analyze-feedback": "POST - Send feedback for analysis",
            "/health": "GET - Health check"
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)