# Starrupture Map Pin Manager

A Flask web application for managing pins on the Starrupture map with coordinate tracking.

Written by CoPilot using chat prompts with the only edits I performed by hand being this paragraph.
This was done as an exercise in using the AI to build an entire program.

## Features

- **Interactive Map**: Click on the map to add pins at specific X,Y coordinates
- **Pin Management**: Add, edit, and delete pins
- **Real-time Coordinates**: View map coordinates as you move your mouse
- **Persistent Storage**: Pins are saved to `pins_data.json`
- **Responsive Design**: Works on desktop and tablet

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Adding a Pin
- **Method 1**: Click on the map at the desired location, adjust coordinates if needed, enter a name, and click "Add Pin"
- **Method 2**: Use the sidebar to manually enter X, Y coordinates and a name

### Editing a Pin
- Click on a pin on the map or in the Pins List
- Modify the name or coordinates in the modal
- Click "Save" to update

### Deleting a Pin
- Click on a pin to open the edit modal
- Click "Delete" to remove the pin

### Viewing Coordinates
- Move your mouse over the map to see real-time X,Y coordinates
- The coordinates change as you hover and update based on the map image dimensions

## Data

Pins are stored in `pins_data.json` with the following structure:
```json
{
  "pin_id": {
    "id": "unique_id",
    "name": "Pin Name",
    "x": 100,
    "y": 200,
    "created": "2024-02-16T10:30:00"
  }
}
```

## API Endpoints

- `GET /api/pins` - Get all pins
- `POST /api/pins` - Create a new pin
- `PUT /api/pins/<id>` - Update a pin
- `DELETE /api/pins/<id>` - Delete a pin

## File Structure

```
scratch/map_builder/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── starrupture_map_outline.png # Map image
├── pins_data.json             # Saved pins (auto-created)
├── templates/
│   └── index.html             # HTML template
└── static/
    ├── style.css              # Styling
    └── app.js                 # JavaScript functionality
```

## Notes

- The map image should be kept in the same directory as `app.py`
- Pins coordinates are based on the actual image dimensions (not display dimensions)
- The application automatically scales coordinates based on how the image is displayed in the browser
