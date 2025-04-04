from flask import Flask, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from canvas_calendar import get_canvas_assignments, get_canvas_schedule
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS with specific options
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5000",  # Local development
            "https://*.github.io",    # GitHub Pages
            "http://127.0.0.1:5000",  # Alternative local development
        ],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'data': '/api/all'
        }
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/all')
def get_all_data():
    try:
        logger.info("Fetching Canvas data...")
        assignments = get_canvas_assignments()
        schedule = get_canvas_schedule()
        logger.info(f"Found {len(assignments)} assignments and {len(schedule)} schedule items")
        
        response_data = {
            'assignments': assignments,
            'schedule': schedule,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 
