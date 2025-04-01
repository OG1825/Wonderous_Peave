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

@app.route('/api/all')
def get_all_data():
    try:
        logger.info("Fetching Canvas data...")
        assignments = get_canvas_assignments()
        schedule = get_canvas_schedule()
        logger.info(f"Found {len(assignments)} assignments and {len(schedule)} schedule items")
        return jsonify({
            'assignments': assignments,
            'schedule': schedule
        })
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return jsonify({
            'error': str(e),
            'assignments': [],
            'schedule': []
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    load_dotenv()  # Load environment variables
    app.run(debug=True, host='0.0.0.0', port=5000) 
