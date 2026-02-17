# Starrupture Map Pin Manager

A Flask web application for managing pins on the Starrupture map with coordinate tracking.

Originally written by CoPilot using chat prompts This was done as an exercise in using the AI to
build an entire program. The map image, starrupture_map_outline.png, was created by me in GIMP 2.
The grid was drawn using a filter and the grid number labels were done mostly by hand but the Y
axis labels were positioned using a script-fu script created by a combination of DuckDuckGo and
Google's AI to copy the text layer and move 50 pixels up. The following script was cobbled together
by me from a few examples provided by both AIs. 
```scheme
(define (copy-layer-up img layer)
    ;; When testing, if no layer selected, this script isn't called.
    ;;(gimp-message "Moving layer")
    (if (= layer -1)
        (gimp-message "No active layer to move.")
        ( let ((copied-layer (car (gimp-layer-copy layer TRUE))))

                (gimp-image-insert-layer img copied-layer 0 -1)
                ;;(gimp-message "Before")
                (let* (
                        (offsets (gimp-drawable-offsets copied-layer))
                        (new-y (- (cadr offsets) 50))
                      )
                  (gimp-layer-set-offsets copied-layer (car offsets) new-y)
                  (gimp-displays-flush)
                )
                ;;(gimp-message "Done.")
        )
    )
)

(script-fu-register
 "copy-layer-up"
 "Copy current layer up by 50 pixels"
 "Copies the active layer and moves up by 50 pixels"
 "Your Name"
 "Your Name"
 "2023"
 ""
 SF-IMAGE    "Image"     0  ; GIMP passes the current image here
 SF-DRAWABLE "Drawable"  0  ; GIMP passes the active layer here
 )

(script-fu-menu-register "copy-layer-up" "<Image>/Scripts")
```

I've started manual changes to the program. Rather than refine the prompt which uses up my free
tier allocation, I'm just making the modification to the code and layout directly.

Within the game, I have cleared most of the fog of war and built a complete map image from multiple
screenshots. I cannot publish that map as it belongs to the owners of StarRupture so I made the
outline. If you want to use the map image from the game, you will have to build the map image
yourself. I set my in-game map zoom to 10 steps from the bottom of the zoom control on a screen
resolution of 1440p. Save the map as "starrupture_map_filled.png" in the same folder as "app.py"
and the program will load that image instead of the outline.

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
