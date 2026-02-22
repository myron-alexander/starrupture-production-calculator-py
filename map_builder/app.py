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
        self.storage_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "storage"
        ]
        self.storage_buildings.sort()

        production_buildings = set()
        production_buildings |= set([b for b in self.crafting_buildings])
        production_buildings |= set([b for b in self.excavator_buildings])
        production_buildings |= set([b for b in self.generator_buildings])
        production_buildings |= set([b for b in self.dispatcher_buildings])
        production_buildings |= set([b for b in self.receiving_buildings])

        self.non_production_buildings = [
            b.building_name for b in self.building_definitions
                if b.building_name not in production_buildings
        ]

        self.item_recipes:dict[str,list[tuple[str, int]]] = {
            ri.item_name: [(r.input_name, r.num_required)
                                for r in self.item_input_definitions
                                    if r.item_name == ri.item_name
                          ]
            for ri in self.item_input_definitions
        }
        """
        Crafting recipe for every craftable item. The key is the craftable item name and the
        value is a list of input items needed to craft the items, as well as the number required to
        craft. The value tuple is (input item name, amount required).
        """

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

    # Convert raw_item_definitions to list of dicts for JSON serialization
    raw_items_list = [
        {
            'item_name': item.item_name,
            'variant': item.variant,
            'items_per_minute': item.items_per_minute,
            'factory': item.factory
        }
        for item in game_data.raw_item_definitions
    ]

    # Convert item_definitions to list of dicts for JSON serialization
    item_defs_list = [
        {
            'item_name': item.item_name,
            'factory': item.factory
        }
        for item in game_data.item_definitions
    ]

    return render_template(
        'index.html',
        valid_raw_items=game_data.valid_raw_items,
        receiving_buildings=game_data.receiving_buildings,
        dispatcher_buildings=game_data.dispatcher_buildings,
        valid_items=game_data.valid_items,
        non_production_buildings=game_data.non_production_buildings,
        storage_buildings=game_data.storage_buildings,
        craftable_items = game_data.craftable_items,
        item_recipes = game_data.item_recipes,
        raw_item_definitions = raw_items_list,
        item_definitions = item_defs_list
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

    site_id = (data.get('name') or '').strip()
    if not site_id:
        return jsonify({'error': 'Site name is required'}), 400

    # Enforce globally unique site id (also guard against legacy name fields)
    for existing_id, existing_pin in pins.items():
        if existing_id == site_id or existing_pin.get('name') == site_id:
            return jsonify({'error': 'Site name must be globally unique'}), 400

    pin_data = {
        'id': site_id,
        'x': data.get('x', 0),
        'y': data.get('y', 0),
        'teleporter': data.get('teleporter', ''),
        'description': data.get('description', ''),
        'resource_nodes': data.get('resource_nodes', {}),
        'cores': data.get('cores', {}),
        'factories': data.get('factories', {}),
        'created': datetime.now().isoformat()
    }

    pins[site_id] = pin_data
    save_pins(pins)

    return jsonify(pin_data), 201

@app.route('/api/pins/<pin_id>', methods=['PUT'])
def update_pin(pin_id):
    """Update a pin (site)."""
    data = request.json
    pins = load_pins()

    if pin_id in pins:
        old_id = pin_id
        # Handle site id rename (site name is the id)
        new_id = pin_id
        if 'name' in data:
            requested_id = (data.get('name') or '').strip()
            if not requested_id:
                return jsonify({'error': 'Site name is required'}), 400
            if requested_id != pin_id:
                for existing_id, existing_pin in pins.items():
                    if existing_id == requested_id:
                        return jsonify({'error': 'Site name must be globally unique'}), 400
                    if existing_id != pin_id and existing_pin.get('name') == requested_id:
                        return jsonify({'error': 'Site name must be globally unique'}), 400
                pin_data = pins.pop(pin_id)
                pin_data['id'] = requested_id
                pins[requested_id] = pin_data
                pin_id = requested_id
                new_id = requested_id

        if old_id != new_id:
            # Update receiver references across all sites
            for pin in pins.values():
                factories = pin.get('factories', {})
                for factory in factories.values():
                    receivers = factory.get('receivers', {})
                    for receiver in receivers.values():
                        if receiver.get('site_id') == old_id:
                            receiver['site_id'] = new_id

        # Update only the fields that are provided
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

        deleted_receivers_count = 0
        if 'factories' in data:
            # Before updating factories, detect deleted dispatchers and cascade delete receivers
            old_factories = pins[pin_id].get('factories', {})
            new_factories = data['factories']

            # Find all dispatchers that were deleted in this site
            deleted_dispatchers = []  # List of (site_id, factory_id, dispatcher_id)
            for factory_id in old_factories:
                if factory_id in new_factories:
                    old_dispatchers = old_factories[factory_id].get('dispatchers', {})
                    new_dispatchers = new_factories[factory_id].get('dispatchers', {})

                    for dispatcher_id in old_dispatchers:
                        if dispatcher_id not in new_dispatchers:
                            deleted_dispatchers.append((pin_id, factory_id, dispatcher_id))

            # Before the receiver deletion operation, copy the new factories. The deletions are
            # done on the pins instance so if data is copied to pins, it will undo the deletions
            # within all factories of pins[pin_id].
            pins[pin_id]['factories'] = data['factories']

            # Delete receivers in ALL factories of ALL sites that reference deleted dispatchers
            if deleted_dispatchers:
                for pin in pins.values():
                    factories = pin.get('factories', {})
                    for factory in factories.values():
                        receivers = factory.get('receivers', {})
                        receivers_to_delete = [
                            rid for rid, receiver in receivers.items()
                            if any(
                                receiver.get('site_id') == disp[0] and
                                receiver.get('factory_id') == disp[1] and
                                receiver.get('dispatcher_id') == disp[2]
                                for disp in deleted_dispatchers
                            )
                        ]
                        deleted_receivers_count += len(receivers_to_delete)
                        for rid in receivers_to_delete:
                            del receivers[rid]

        # Remove legacy name field if present
        if 'name' in pins[pin_id]:
            del pins[pin_id]['name']

        pins[pin_id]['id'] = new_id

        save_pins(pins)

        # Return response with deleted receivers count if applicable
        response_data = pins[pin_id].copy()
        if deleted_receivers_count > 0:
            response_data['deleted_receivers'] = deleted_receivers_count
        return jsonify(response_data)

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

    #dump_game_data()

#---------------------------------------------------------------------------------------------------

def main():
    load_game_data()
    app.run(debug=True, port=5000)

#---------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

#---------------------------------------------------------------------------------------------------
