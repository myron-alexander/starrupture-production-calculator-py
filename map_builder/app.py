"""
Flask application for managing pins on a map grid with coordinates.
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
PINS_FILE = 'pins_data.json'
MAP_IMAGE = 'starrupture_map_outline.png'

# Initialize pins storage
def load_pins():
    """Load pins from JSON file."""
    if os.path.exists(PINS_FILE):
        with open(PINS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_pins(pins):
    """Save pins to JSON file."""
    with open(PINS_FILE, 'w') as f:
        json.dump(pins, f, indent=2)

# Routes
@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/map-image')
def map_image():
    """Serve the map image."""
    return send_file(MAP_IMAGE, mimetype='image/png')

@app.route('/api/pins', methods=['GET'])
def get_pins():
    """Get all pins."""
    pins = load_pins()
    return jsonify(pins)

@app.route('/api/pins', methods=['POST'])
def add_pin():
    """Add a new pin."""
    data = request.json
    pins = load_pins()
    
    pin_id = str(int(datetime.now().timestamp() * 1000))
    pin_data = {
        'id': pin_id,
        'name': data.get('name', 'Unnamed Pin'),
        'x': data.get('x', 0),
        'y': data.get('y', 0),
        'created': datetime.now().isoformat()
    }
    
    pins[pin_id] = pin_data
    save_pins(pins)
    
    return jsonify(pin_data), 201

@app.route('/api/pins/<pin_id>', methods=['PUT'])
def update_pin(pin_id):
    """Update a pin."""
    data = request.json
    pins = load_pins()
    
    if pin_id in pins:
        pins[pin_id].update({
            'name': data.get('name', pins[pin_id]['name']),
            'x': data.get('x', pins[pin_id]['x']),
            'y': data.get('y', pins[pin_id]['y'])
        })
        save_pins(pins)
        return jsonify(pins[pin_id])
    
    return jsonify({'error': 'Pin not found'}), 404

@app.route('/api/pins/<pin_id>', methods=['DELETE'])
def delete_pin(pin_id):
    """Delete a pin."""
    pins = load_pins()
    
    if pin_id in pins:
        del pins[pin_id]
        save_pins(pins)
        return jsonify({'message': 'Pin deleted'}), 200
    
    return jsonify({'error': 'Pin not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
