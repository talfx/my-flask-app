from flask import Flask, request, jsonify
from anthropic import Anthropic
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Claude client
client = Anthropic()

@app.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    try:
        data = request.json
        print("=" * 50)
        print("DATA RECEIVED:")
        print(data)
        print("=" * 50)
        
        return jsonify({
            "status": "received",
            "data": data
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API documentation"""
    return jsonify({
        "service": "AI-Powered Feedback Analyzer",
        "version": "1.0",
        "endpoints": {
            "/analyze-feedback": "POST - Send feedback for analysis"
        },
        "usage": {
            "method": "POST",
            "url": "/analyze-feedback",
            "body": {
                "feedback": [
                    {"name": "Alice", "feedback": "Sample feedback"},
                    {"name": "Bob", "feedback": "Another feedback"}
                ]
            }
        }
    }), 200


if __name__ == '__main__':
    # Run in development mode
    app.run(debug=True, host='localhost', port=5000)

    
