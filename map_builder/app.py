"""
Flask application for managing pins on a map grid with coordinates.
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import tempfile
import fcntl
import copy
from contextlib import contextmanager
from threading import RLock
from datetime import datetime
from visualizer import visualize_factory_on_a_grid
from application_data import *

#---------------------------------------------------------------------------------------------------

game_data = None

#---------------------------------------------------------------------------------------------------

app = Flask(__name__)

# Configuration
PINS_FILE = 'pins_data.json'
MAP_IMAGE = 'starrupture_map_outline.png'
FILLED_MAP_IMAGE = 'starrupture_map_filled.png'
PINS_WRITE_LOCK = RLock()
PINS_LOCK_FILE = f'{PINS_FILE}.lock'
PINS_CACHE = None

def get_map_image_filename() -> str:
    return FILLED_MAP_IMAGE if os.path.exists(FILLED_MAP_IMAGE) else MAP_IMAGE

def _persist_pins_to_file(pins):
    """Persist pins atomically and durably. Caller is responsible for synchronization."""
    pins_dir = os.path.dirname(os.path.abspath(PINS_FILE)) or '.'

    fd, temp_path = tempfile.mkstemp(prefix='pins_', suffix='.tmp', dir=pins_dir, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(pins, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, PINS_FILE)

        dir_fd = os.open(pins_dir, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def _normalize_receiver_dispatchers(pins) -> bool:
    """Normalize receiver linkage to the `dispatchers` list model; returns True when changed."""
    if not isinstance(pins, dict):
        return False

    changed = False

    for pin in pins.values():
        if not isinstance(pin, dict):
            continue

        factories = pin.get('factories', {})
        if not isinstance(factories, dict):
            continue

        for factory in factories.values():
            if not isinstance(factory, dict):
                continue

            receivers = factory.get('receivers', {})
            if not isinstance(receivers, dict):
                continue

            for receiver in receivers.values():
                if not isinstance(receiver, dict):
                    continue

                refs = []
                dispatchers = receiver.get('dispatchers', [])

                if isinstance(dispatchers, list):
                    for ref in dispatchers:
                        if not isinstance(ref, dict):
                            continue
                        site_id = (ref.get('site_id') or '').strip()
                        factory_id = (ref.get('factory_id') or '').strip()
                        dispatcher_id = (ref.get('dispatcher_id') or '').strip()
                        if site_id and factory_id and dispatcher_id:
                            refs.append({
                                'site_id': site_id,
                                'factory_id': factory_id,
                                'dispatcher_id': dispatcher_id,
                            })

                # Legacy fallback: single receiver link fields.
                if not refs:
                    legacy_site_id = (receiver.get('site_id') or '').strip()
                    legacy_factory_id = (receiver.get('factory_id') or '').strip()
                    legacy_dispatcher_id = (receiver.get('dispatcher_id') or '').strip()
                    if legacy_site_id and legacy_factory_id and legacy_dispatcher_id:
                        refs.append({
                            'site_id': legacy_site_id,
                            'factory_id': legacy_factory_id,
                            'dispatcher_id': legacy_dispatcher_id,
                        })

                deduped_refs = []
                seen = set()
                for ref in refs:
                    key = (ref['site_id'], ref['factory_id'], ref['dispatcher_id'])
                    if key in seen:
                        continue
                    seen.add(key)
                    deduped_refs.append(ref)

                if receiver.get('dispatchers') != deduped_refs:
                    receiver['dispatchers'] = deduped_refs
                    changed = True

                if 'site_id' in receiver:
                    receiver.pop('site_id', None)
                    changed = True
                if 'factory_id' in receiver:
                    receiver.pop('factory_id', None)
                    changed = True
                if 'dispatcher_id' in receiver:
                    receiver.pop('dispatcher_id', None)
                    changed = True

    return changed

# Initialize pins storage
def _load_pins_from_file():
    """Load pins from JSON file."""
    if os.path.exists(PINS_FILE):
        with open(PINS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_pins():
    """Load pins from synchronized in-memory cache."""
    global PINS_CACHE

    with PINS_WRITE_LOCK:
        if PINS_CACHE is None:
            PINS_CACHE = _load_pins_from_file()
            if _normalize_receiver_dispatchers(PINS_CACHE):
                _persist_pins_to_file(PINS_CACHE)
        return copy.deepcopy(PINS_CACHE)

@contextmanager
def pins_transaction_lock():
    with PINS_WRITE_LOCK:
        with open(PINS_LOCK_FILE, 'a', encoding='utf-8') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

def save_pins(pins):
    """Write-through save: update cache, then persist synchronously and durably."""
    global PINS_CACHE

    with PINS_WRITE_LOCK:
        PINS_CACHE = copy.deepcopy(pins)
        _persist_pins_to_file(PINS_CACHE)

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
            'items_per_minute': item.items_per_minute,
            'factory': item.factory
        }
        for item in game_data.item_definitions
    ]

    response = render_template(
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

    # Disable caching for the main page to ensure template variables are always fresh
    from flask import make_response
    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

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
    with pins_transaction_lock():
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

#---------------------------------------------------------------------------------------------------

@app.route('/api/pins/<pin_id>', methods=['PUT'])
def update_pin(pin_id):
    """Update a pin (site)."""
    data = request.json
    with pins_transaction_lock():
        pins = load_pins()

        #print("data:")
        #print(data)

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
                            updated_refs = []
                            refs = receiver.get('dispatchers', [])

                            if isinstance(refs, list):
                                for ref in refs:
                                    if not isinstance(ref, dict):
                                        continue
                                    ref_site_id = ref.get('site_id')
                                    if ref_site_id == old_id:
                                        ref['site_id'] = new_id
                                    if ref.get('site_id') and ref.get('factory_id') and ref.get('dispatcher_id'):
                                        updated_refs.append(ref)

                            # Legacy single dispatcher fields fallback.
                            if not updated_refs:
                                legacy_site_id = receiver.get('site_id')
                                legacy_factory_id = receiver.get('factory_id')
                                legacy_dispatcher_id = receiver.get('dispatcher_id')
                                if legacy_site_id == old_id:
                                    legacy_site_id = new_id
                                if legacy_site_id and legacy_factory_id and legacy_dispatcher_id:
                                    updated_refs.append({
                                        'site_id': legacy_site_id,
                                        'factory_id': legacy_factory_id,
                                        'dispatcher_id': legacy_dispatcher_id,
                                    })

                            if updated_refs:
                                # Deduplicate and normalize to the current model shape.
                                deduped_refs = []
                                seen = set()
                                for ref in updated_refs:
                                    key = (ref['site_id'], ref['factory_id'], ref['dispatcher_id'])
                                    if key in seen:
                                        continue
                                    seen.add(key)
                                    deduped_refs.append(ref)
                                receiver['dispatchers'] = deduped_refs
                                # Remove legacy single dispatcher fields if present.
                                receiver.pop('site_id', None)
                                receiver.pop('factory_id', None)
                                receiver.pop('dispatcher_id', None)

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
                # Before updating factories, detect deleted dispatchers and remove references in
                # receivers.
                old_factories = pins[pin_id].get('factories', {})
                new_factories = data['factories']

                # MA: Renaming a dispatcher will be picked up as a deletion so all the receivers
                #     will be deleted. I think a new route needs to be added to the API to allow
                #     for updating the dispatcher independant of other factors. This will allow
                #     a rename to update references instead of deleting them.
                #
                # Update: I was wrong, the javascript updates all the references then saves
                #         every factory in all sites, including those that haven't changed.
                #         Forgot that the change was being made in the javascript.
                #         When the AI wrote this, it sometimes made the changes in the javascript and
                #         sometimes on the server.

                # Find all dispatchers that were deleted in this site
                deleted_dispatchers = []  # List of (site_id, factory_id, dispatcher_id)
                for factory_id in old_factories:
                    if factory_id in new_factories:
                        old_dispatchers = old_factories[factory_id].get('dispatchers', {})
                        new_dispatchers = new_factories[factory_id].get('dispatchers', {})

                        for dispatcher_id in old_dispatchers:
                            if dispatcher_id not in new_dispatchers:
                                deleted_dispatchers.append((pin_id, factory_id, dispatcher_id))

                # Before the receiver modification operation, copy the new factories. The deletions are
                # done on the pins instance so if data is copied to pins, it will undo the deletions
                # within all factories of pins[pin_id].
                pins[pin_id]['factories'] = data['factories']

                # Update receivers in ALL factories of ALL sites that reference deleted dispatchers
                if deleted_dispatchers:
                    for pin in pins.values():
                        factories = pin.get('factories', {})
                        for factory in factories.values():
                            receivers = factory.get('receivers', {})

                            for rid, receiver in receivers.items():
                                refs = receiver.get('dispatchers', [])
                                normalized_refs = []

                                if isinstance(refs, list):
                                    for ref in refs:
                                        if not isinstance(ref, dict):
                                            continue
                                        if ref.get('site_id') and ref.get('factory_id') and ref.get('dispatcher_id'):
                                            normalized_refs.append({
                                                'site_id': ref.get('site_id'),
                                                'factory_id': ref.get('factory_id'),
                                                'dispatcher_id': ref.get('dispatcher_id'),
                                            })

                                # Legacy single dispatcher fields fallback.
                                if not normalized_refs:
                                    legacy_site_id = receiver.get('site_id')
                                    legacy_factory_id = receiver.get('factory_id')
                                    legacy_dispatcher_id = receiver.get('dispatcher_id')
                                    if legacy_site_id and legacy_factory_id and legacy_dispatcher_id:
                                        normalized_refs.append({
                                            'site_id': legacy_site_id,
                                            'factory_id': legacy_factory_id,
                                            'dispatcher_id': legacy_dispatcher_id,
                                        })

                                filtered_refs = [
                                    ref for ref in normalized_refs
                                    if not any(
                                        ref['site_id'] == disp[0] and
                                        ref['factory_id'] == disp[1] and
                                        ref['dispatcher_id'] == disp[2]
                                        for disp in deleted_dispatchers
                                    )
                                ]

                                if len(filtered_refs) < len(normalized_refs):
                                    deduped_refs = []
                                    if filtered_refs:
                                        seen = set()
                                        for ref in filtered_refs:
                                            key = (ref['site_id'], ref['factory_id'], ref['dispatcher_id'])
                                            if key in seen:
                                                continue
                                            seen.add(key)
                                            deduped_refs.append(ref)
                                    print(f"Updating receiver '{rid}' refs: norm:{len(normalized_refs)} filt:{len(filtered_refs)} ddup:{len(deduped_refs)}. from {refs} to {deduped_refs}.")
                                    receiver['dispatchers'] = deduped_refs
                                    # Remove legacy single dispatcher fields if present.
                                    receiver.pop('site_id', None)
                                    receiver.pop('factory_id', None)
                                    receiver.pop('dispatcher_id', None)

            # Remove legacy name field if present
            if 'name' in pins[pin_id]:
                del pins[pin_id]['name']

            pins[pin_id]['id'] = new_id

            #print(pins)

            save_pins(pins)

            # Return response with deleted receivers count if applicable
            response_data = pins[pin_id].copy()
            if deleted_receivers_count > 0:
                response_data['deleted_receivers'] = deleted_receivers_count
            return jsonify(response_data)

    return jsonify({'error': 'Pin not found'}), 404

#---------------------------------------------------------------------------------------------------

@app.route('/api/pins/<pin_id>', methods=['DELETE'])
def delete_pin(pin_id):
    """Delete a pin."""
    with pins_transaction_lock():
        pins = load_pins()

        if pin_id in pins:
            del pins[pin_id]
            save_pins(pins)
            return jsonify({'message': 'Pin deleted'}), 200

    return jsonify({'error': 'Pin not found'}), 404

#---------------------------------------------------------------------------------------------------

@app.route('/api/pins/<pin_id>/<factory_id>/dispatchers/<dispatcher_id>', methods=['POST'])
def update_dispatcher(pin_id, factory_id, dispatcher_id):
    """
    Update dispatcher separate from other elements so that renaming a dispatcher will allow
    for updating receivers that reference the dispatcher instead of deleting them as what
    would happen in update_pin.

    Expecting request data:
    {
        new_id: str
                Optional. When present, the ID of the dispatcher must be changed. Must be omitted
                when an ID change is not intended.

        dispatched_item: str
                Name of the dispatched item. Must match an item name in the game data.

        output_rate_limit_ipm: int
                Maximum rate, in items per minute, that items can be dispatched.

        input_rate_limit_ipm: int
                Maximum rate, in items per minute, that items can be received for dispatching from
                the item sources.

        from_ids: list[str]
                Ids of the suppliers that provide dispatched item.

        building_id: str
                When the dispatcher is a building instead of a rail, the ID of the building in the
                game data. When the dispatcher is not a building, this is empty.
    }
    """
    data = request.json
    pins = load_pins()

    # The reason for having the rename changes done in the javascript, as well as most of the
    # functionality there, is that it scales very well.
    #
    # The reason for having the rename changes done on the server is that the server has more
    # flexibility with data modifications. For example, if this was a database backed application,
    # the rename could be done with a few update statements in the database while pushing all the
    # changes from the javascript either requires more REST interfaces, or, as what the AI created,
    # forcing a data save for everything, even those that haven't changed.
    #
    # The middle point is having the javascript perform the changes to the data, but instead of
    # saving all the data, only push the changes. This makes the application more complex.
    #
    # Ultimately, the methodology must be determined by the requirments of the environment and
    # behaviours. For this application, scaling is not an issue so having more of the functionlity
    # on the server side makes more sense.


    # TODO: Add implementation.

    # 1. Changing the dispatcher_id is identified by reading the key "new_id" that will only
    #    be present if an id change is requested.
    # 2. If an id change is requested, locate all references in pins and update them.
    # 3. Update the dispatcher details similar to update_pins.
    # 4. Save pins.
    # 5. Return the entire pins.

    response_data = pins.copy()
    return jsonify(response_data), 200

#---------------------------------------------------------------------------------------------------

@app.route('/api/pins/<pin_id>/<factory_id>/visdata', methods=['GET'])
def visualize_factory(pin_id, factory_id):
    """Generate a SVG visualization of factory nodes."""
    pins = load_pins()
    svg_data = visualize_factory_on_a_grid(pins, pin_id, factory_id)
    if svg_data is None:
        return jsonify(error="Factory is empty"), 404
    else:
        return jsonify({'svgStyles': svg_data[3], 'svgContent': svg_data[2]}), 200


#---------------------------------------------------------------------------------------------------

@app.route('/api/pins/<pin_id>/<factory_id>/visualization', methods=['GET'])
def render_visualize_factory(pin_id, factory_id):
    """Generate a SVG visualization of factory nodes."""
    pins = load_pins()

    site = pins.get(pin_id)
    if site is None:
        return jsonify({'error': 'Pin not found'}), 404
    factory = site["factories"].get(factory_id)
    if factory is None:
        return jsonify({'error': f"Factory of '{pin_id}' not found"}), 404

    purpose = factory.get("purpose", "No purpose set")

    svg_data = visualize_factory_on_a_grid(pins, pin_id, factory_id, game_data) # type: ignore

    html_styles = """
body {
    font-family: monospace;
    background: #1e1e1e;
    color: #e0e0e0;
    padding: 20px;
    margin: 0;
}
.container {
    max-width: 100%;
    margin: 0 auto;
}
.factory-header {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #4fc3f7;
}
.factory-purpose {
    font-size: 14px;
    color: #90caf9;
    margin-bottom: 30px;
    font-style: italic;
}
.visualization-wrapper {
    /*overflow: auto;*/    /* OR limit the viewable SVG width and scroll the SVG within the wrapper. */
    display: inline-block; /* OR fit the wrapper to the svg. */
    border: 1px solid #3a3a4a;
    border-radius: 4px;
    background: #2a2a2a;
}
"""


    if svg_data is None:
        svg_styles = ""
        svg_content = "<p>Factory is empty.</p>"
    else:
        svg_styles = svg_data[3]
        svg_content = svg_data[2]

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>"{pin_id}"/"{factory_id}" visualization</title>
    <style>
    {html_styles}
    {svg_styles}
    </style>
</head>
<body>
    <div class="container">
        <div class="factory-header">'{pin_id}'/'{factory_id}'</div>
        <div class="factory-purpose">{purpose}</div>
        <div class="visualization-wrapper">
            {svg_content}
        </div>
    </div>
</body>
</html>
"""

    return html, 200

#---------------------------------------------------------------------------------------------------

def main():
    global game_data
    game_data = load_game_data()
    app.run(debug=True, port=5000)

#---------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

#---------------------------------------------------------------------------------------------------
