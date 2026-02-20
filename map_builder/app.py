"""
Flask application for managing pins on a map grid with coordinates.
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import sys
from datetime import datetime

sys.path.append("..")

from starrupture.sr_game_data import *

#---------------------------------------------------------------------------------------------------

class GameData:
    def __init__(
            self,
            items:list[ItemRecord],
            inputs:list[RecipeInputRecord],
            raw_items:list[RawItemRecord],
            buildings:list[BuildingRecord]) -> None:

        self.item_definitions = items
        self.item_input_definitions = inputs
        self.raw_item_definitions = raw_items
        self.building_definitions = buildings

        self.item_definitions.sort(key=lambda i: i.item_name.lower())
        self.item_input_definitions.sort(key=lambda i: f"{i.item_name};{i.input_name}".lower())
        self.raw_item_definitions.sort(key=lambda i: f"{i.item_name};{i.variant}".lower())
        self.building_definitions.sort(key=lambda i: i.building_name)

        self.craftable_items = list(set([i.item_name for i in self.item_input_definitions]))
        self.craftable_items.sort()
        self.valid_items = self._make_valid_items()
        self.valid_raw_items = list(set([i.item_name for i in self.raw_item_definitions]))
        self.valid_raw_items.sort()
        self.valid_raw_variations = list(set(i.variant for i in self.raw_item_definitions))
        self.valid_raw_variations.sort()
        self.crafting_buildings = list(set([i.factory for i in self.item_definitions]))
        self.crafting_buildings.sort()
        self.excavator_buildings = list(set([i.factory for i in self.raw_item_definitions]))
        self.excavator_buildings.sort()
        self.non_production_buildings = [
            b for b in self.building_definitions 
                if b.building_name not in self.crafting_buildings 
                    or b.building_name not in self.excavator_buildings
        ]
        self.generator_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "generator"
        ]
        self.generator_buildings.sort()
        self.dispatcher_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "dispatcher"
        ]
        self.dispatcher_buildings.sort()
        self.receiving_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "receiver"
        ]
        self.receiving_buildings.sort()

    #---------------------------------------------------------------------------

    def _make_valid_items(self) -> list[str]:
        valid_items = set()
        valid_items |= set([i.item_name for i in self.item_definitions])
        valid_items |= set([i.item_name for i in self.raw_item_definitions])
        l = list(valid_items)
        l.sort()
        return l

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

game_data = None

#---------------------------------------------------------------------------------------------------

app = Flask(__name__)

# Configuration
PINS_FILE = 'pins_data.json'
MAP_IMAGE = 'starrupture_map_outline.png'
FILLED_MAP_IMAGE = 'starrupture_map_filled.png'

def get_map_image_filename() -> str:
    return FILLED_MAP_IMAGE if os.path.exists(FILLED_MAP_IMAGE) else MAP_IMAGE

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
    if game_data is None:
        load_game_data()
    return render_template(
        'index.html',
        valid_raw_items=game_data.valid_raw_items,
        receiving_buildings=game_data.receiving_buildings,
        dispatcher_buildings=game_data.dispatcher_buildings,
        valid_items=game_data.valid_items
    )

@app.route('/map-image')
def map_image():
    """Serve the map image."""
    return send_file(get_map_image_filename(), mimetype='image/png')

@app.route('/api/pins', methods=['GET'])
def get_pins():
    """Get all pins."""
    pins = load_pins()
    return jsonify(pins)

@app.route('/api/pins', methods=['POST'])
def add_pin():
    """Add a new pin (site)."""
    data = request.json
    pins = load_pins()

    pin_id = str(int(datetime.now().timestamp() * 1000))
    pin_data = {
        'id': pin_id,
        'name': data.get('name', 'Unnamed Site'),
        'x': data.get('x', 0),
        'y': data.get('y', 0),
        'teleporter': data.get('teleporter', ''),
        'description': data.get('description', ''),
        'resource_nodes': data.get('resource_nodes', {}),
        'cores': data.get('cores', {}),
        'factories': data.get('factories', {}),
        'created': datetime.now().isoformat()
    }

    pins[pin_id] = pin_data
    save_pins(pins)

    return jsonify(pin_data), 201

@app.route('/api/pins/<pin_id>', methods=['PUT'])
def update_pin(pin_id):
    """Update a pin (site)."""
    data = request.json
    pins = load_pins()

    if pin_id in pins:
        # Update only the fields that are provided
        if 'name' in data:
            pins[pin_id]['name'] = data['name']
        if 'x' in data:
            pins[pin_id]['x'] = data['x']
        if 'y' in data:
            pins[pin_id]['y'] = data['y']
        if 'teleporter' in data:
            pins[pin_id]['teleporter'] = data['teleporter']
        if 'description' in data:
            pins[pin_id]['description'] = data['description']
        if 'resource_nodes' in data:
            pins[pin_id]['resource_nodes'] = data['resource_nodes']
        if 'cores' in data:
            pins[pin_id]['cores'] = data['cores']
        if 'factories' in data:
            pins[pin_id]['factories'] = data['factories']

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


#---------------------------------------------------------------------------------------------------

def dump_game_data():
    print(game_data.craftable_items)

#---------------------------------------------------------------------------------------------------

def load_game_data():

    items, inputs, raws, buildings = load_definitions(
            '../starrupture_recipe_items.csv',
            '../starrupture_recipe_input.csv',
            '../starrupture_recipe_raw.csv',
            '../starrupture_recipe_buildings.csv'
    )

    global game_data
    game_data = GameData(items, inputs, raws, buildings)

    dump_game_data()

#---------------------------------------------------------------------------------------------------

def main():
    load_game_data()
    app.run(debug=True, port=5000)

#---------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

#---------------------------------------------------------------------------------------------------
