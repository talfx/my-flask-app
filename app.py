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
        
        # Validate input
        if not data or 'feedback' not in data:
            return jsonify({"error": "Missing 'feedback' key in request"}), 400
        
        feedback_list = data['feedback']
        
        if not isinstance(feedback_list, list) or len(feedback_list) == 0:
            return jsonify({"error": "Feedback must be a non-empty list"}), 400
        
        # Format feedback for Claude
        formatted_feedback = "\n".join([
            f"- {item.get('name', 'Anonymous')}: {item.get('feedback', '')}"
            for item in feedback_list
        ])
        print(formatted_feedback)
        
        # Create prompt for Claude
#         prompt = f"""Analyze the following customer feedback and provide:
# 1. A summary of key themes
# 2. Top 3 positive points (if any)
# 3. Top 3 negative points (if any)
# 4. One specific improvement suggestion
# 5. Sentiment classification for each piece of feedback (Positive/Negative/Neutral)

# Format your response as JSON with these keys:
# - summary: brief overall summary
# - positive_points: list of top positive points
# - negative_points: list of top negative points
# - improvement_suggestion: one actionable improvement
# - sentiment_breakdown: list with name and sentiment for each feedback

# Customer Feedback:
# {formatted_feedback}"""
        
        # Call Claude API
        # message = client.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=1024,
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        
        # # Extract response
        # response_text = message.content[0].text
        
        # # Try to parse as JSON, if it fails return as text
        # try:
        #     import json
        #     analysis = json.loads(response_text)
        # except json.JSONDecodeError:
        #     # If Claude didn't return pure JSON, extract it
        #     analysis = {
        #         "summary": response_text,
        #         "raw_response": response_text
        #     }
        
        # # Format final response
        # result = {
        #     "status": "success",
        #     "timestamp": datetime.now().isoformat(),
        #     "feedback_count": len(feedback_list),
        #     "analysis": analysis
        # }
        
        # return jsonify(result), 200
        return formatted_feedback
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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
    