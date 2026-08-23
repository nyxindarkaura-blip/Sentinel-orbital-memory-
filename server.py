"""
server.py
---------
Flask backend server for the SENTINEL + ORBITAL MEMORY dashboard.
Exposes two JSON API configurations (nominal and anomaly) and serves the static
cockpit dashboard frontend (index.html, style.css, script.js).

Usage:
    pip install -r requirements-ui.txt
    python server.py
"""

import os
import sys
from flask import Flask, jsonify, request

# Ensure the src directory is in the path to load the backend modules correctly
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.append(src_path)

from telemetry_simulator import generate_demo_stream, generate_normal_telemetry
from sentinel import run_sentinel
from orbital_memory import find_similar_events
from synthesis import build_risk_card

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    """Serves the main static UI index page."""
    return app.send_static_file('index.html')

@app.route('/api/simulate')
def simulate():
    """Exposes the telemetry simulation and risk diagnosis pipeline as a JSON API."""
    mode = request.args.get('mode', 'anomaly')
    
    if mode == 'nominal':
        # Generate 60 minutes of normal telemetry (within baseline ranges)
        readings = generate_normal_telemetry(minutes=60, start_minute=0)
    else:
        # Generate 30 minutes normal + 30 minutes anomalous telemetry
        readings = generate_demo_stream()
        
    sentinel_result = run_sentinel(readings)
    diagnosis = sentinel_result["diagnosis"]
    matches = find_similar_events(diagnosis["flagged_signals"])
    card = build_risk_card(sentinel_result, matches)
    
    return jsonify({
        "readings": readings,
        "sentinel_result": sentinel_result,
        "matches": matches,
        "card": card
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SENTINEL + ORBITAL MEMORY incident response server running.")
    print("Open http://localhost:5000 in your browser to view the cockpit dashboard.")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
