from flask import Flask, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from canvas_calendar import get_canvas_assignments, get_canvas_schedule

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
        assignments = get_canvas_assignments()
        schedule = get_canvas_schedule()
        return jsonify({
            'assignments': assignments,
            'schedule': schedule
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
