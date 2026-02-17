// DOM Elements
const mapContainer = document.getElementById('mapContainer');
const mapImage = document.getElementById('mapImage');
const pinsOverlay = document.getElementById('pinsOverlay');
const coordXDisplay = document.getElementById('coordX');
const coordYDisplay = document.getElementById('coordY');
const pinNameInput = document.getElementById('pinName');
const pinXInput = document.getElementById('pinX');
const pinYInput = document.getElementById('pinY');
const addPinBtn = document.getElementById('addPinBtn');
const pinsList = document.getElementById('pinsList');
const editModal = document.getElementById('editModal');
const closeBtn = document.querySelector('.close');
const savePinBtn = document.getElementById('savePinBtn');
const deletePinBtn = document.getElementById('deletePinBtn');
const editPinName = document.getElementById('editPinName');
const editPinX = document.getElementById('editPinX');
const editPinY = document.getElementById('editPinY');

let pins = {};
let selectedPinId = null;

// Grid configuration
const GRID_ORIGIN_X = 350;  // Pixel X coordinate of grid origin
const GRID_ORIGIN_Y = 1650; // Pixel Y coordinate of grid origin
const GRID_SPACING = 50;    // Pixels between grid lines

// Convert pixel coordinates to grid coordinates
// Y coordinates increase going UP the grid (inverted from pixel Y)
function pixelToGrid(pixelX, pixelY) {
    const gridX = Math.round((pixelX - GRID_ORIGIN_X) / GRID_SPACING);
    const gridY = Math.round((GRID_ORIGIN_Y - pixelY) / GRID_SPACING);
    return { gridX, gridY };
}

// Convert grid coordinates to pixel coordinates
// Y coordinates increase going UP the grid (inverted from pixel Y)
function gridToPixel(gridX, gridY) {
    const pixelX = gridX * GRID_SPACING + GRID_ORIGIN_X;
    const pixelY = GRID_ORIGIN_Y - (gridY * GRID_SPACING);
    return { pixelX, pixelY };
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    mapImage.onload = () => {
        loadPins();
        attachEventListeners();
    };
});

function attachEventListeners() {
    // Map click to add pins
    mapContainer.addEventListener('click', handleMapClick);
    
    // Mouse move to show coordinates
    mapContainer.addEventListener('mousemove', handleMouseMove);
    
    // Add pin button
    addPinBtn.addEventListener('click', handleAddPin);
    
    // Modal controls
    closeBtn.addEventListener('click', closeEditModal);
    savePinBtn.addEventListener('click', handleSavePin);
    deletePinBtn.addEventListener('click', handleDeletePin);
    
    window.addEventListener('click', (event) => {
        if (event.target === editModal) {
            closeEditModal();
        }
    });
}

function handleMapClick(event) {
    const overlayRect = pinsOverlay.getBoundingClientRect();
    
    // Get click position relative to image
    const clickX = event.clientX - overlayRect.left;
    const clickY = event.clientY - overlayRect.top;
    
    // Scale to image coordinates
    const imageWidth = mapImage.naturalWidth;
    const imageHeight = mapImage.naturalHeight;
    const displayWidth = mapImage.clientWidth;
    const displayHeight = mapImage.clientHeight;
    
    const scaleX = imageWidth / displayWidth;
    const scaleY = imageHeight / displayHeight;
    
    const pixelX = clickX * scaleX;
    const pixelY = clickY * scaleY;
    
    // Convert to grid coordinates and snap to grid
    const { gridX, gridY } = pixelToGrid(pixelX, pixelY);
    
    // Update input fields with grid coordinates
    pinXInput.value = gridX;
    pinYInput.value = gridY;
}

function handleMouseMove(event) {
    const overlayRect = pinsOverlay.getBoundingClientRect();
    
    const moveX = event.clientX - overlayRect.left;
    const moveY = event.clientY - overlayRect.top;
    
    const imageWidth = mapImage.naturalWidth;
    const imageHeight = mapImage.naturalHeight;
    const displayWidth = mapImage.clientWidth;
    const displayHeight = mapImage.clientHeight;
    
    const scaleX = imageWidth / displayWidth;
    const scaleY = imageHeight / displayHeight;
    
    const pixelX = moveX * scaleX;
    const pixelY = moveY * scaleY;
    
    // Convert to grid coordinates
    const { gridX, gridY } = pixelToGrid(pixelX, pixelY);
    
    coordXDisplay.textContent = gridX;
    coordYDisplay.textContent = gridY;
}

async function handleAddPin() {
    const name = pinNameInput.value.trim();
    let x = parseInt(pinXInput.value);
    let y = parseInt(pinYInput.value);
    
    if (!name) {
        alert('Please enter a pin name');
        return;
    }
    
    // Validate grid coordinates
    if (isNaN(x) || isNaN(y)) {
        alert('Invalid grid coordinates');
        return;
    }
    
    try {
        const response = await fetch('/api/pins', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, x, y })
        });
        
        if (response.ok) {
            const pin = await response.json();
            pins[pin.id] = pin;
            renderPins();
            renderPinsList();
            
            // Reset form
            pinNameInput.value = 'New Location';
            pinXInput.value = 0;
            pinYInput.value = 0;
        }
    } catch (error) {
        console.error('Error adding pin:', error);
        alert('Error adding pin');
    }
}

async function loadPins() {
    try {
        const response = await fetch('/api/pins');
        pins = await response.json();
        renderPins();
        renderPinsList();
    } catch (error) {
        console.error('Error loading pins:', error);
    }
}

function renderPins() {
    pinsOverlay.innerHTML = '';
    
    const imageWidth = mapImage.naturalWidth;
    const imageHeight = mapImage.naturalHeight;
    const displayWidth = mapImage.clientWidth;
    const displayHeight = mapImage.clientHeight;
    
    Object.values(pins).forEach((pin, index) => {
        // Convert grid coordinates to pixel coordinates
        const { pixelX, pixelY } = gridToPixel(pin.x, pin.y);
        
        // Scale to display coordinates
        const displayX = (pixelX / imageWidth) * displayWidth;
        const displayY = (pixelY / imageHeight) * displayHeight;
        
        const pinElement = document.createElement('div');
        pinElement.className = 'pin';
        pinElement.style.left = displayX + 'px';
        pinElement.style.top = displayY + 'px';
        pinElement.textContent = index + 1;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'pin-tooltip';
        tooltip.innerHTML = `<strong>${pin.name}</strong><br>Grid: (${pin.x}, ${pin.y})`;
        
        pinElement.appendChild(tooltip);
        pinElement.addEventListener('click', (e) => {
            e.stopPropagation();
            openEditModal(pin.id);
        });
        
        pinsOverlay.appendChild(pinElement);
    });
}

function renderPinsList() {
    pinsList.innerHTML = '';
    
    if (Object.keys(pins).length === 0) {
        pinsList.innerHTML = '<div class="pin-item empty">No pins yet</div>';
        return;
    }
    
    Object.entries(pins).forEach(([id, pin], index) => {
        const pinItem = document.createElement('div');
        pinItem.className = 'pin-item';
        pinItem.innerHTML = `
            <div class="pin-item-name">${index + 1}. ${pin.name}</div>
            <div class="pin-item-coords">Grid: (${pin.x}, ${pin.y})</div>
        `;
        pinItem.addEventListener('click', () => openEditModal(id));
        pinsList.appendChild(pinItem);
    });
}

function openEditModal(pinId) {
    selectedPinId = pinId;
    const pin = pins[pinId];
    
    editPinName.value = pin.name;
    editPinX.value = pin.x;
    editPinY.value = pin.y;
    
    editModal.classList.add('show');
}

function closeEditModal() {
    editModal.classList.remove('show');
    selectedPinId = null;
}

async function handleSavePin() {
    if (!selectedPinId) return;
    
    const name = editPinName.value.trim();
    const x = parseInt(editPinX.value);
    const y = parseInt(editPinY.value);
    
    if (!name) {
        alert('Please enter a pin name');
        return;
    }
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, x, y })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeEditModal();
        }
    } catch (error) {
        console.error('Error saving pin:', error);
        alert('Error saving pin');
    }
}

async function handleDeletePin() {
    if (!selectedPinId) return;
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            delete pins[selectedPinId];
            renderPins();
            renderPinsList();
            closeEditModal();
        }
    } catch (error) {
        console.error('Error deleting pin:', error);
        alert('Error deleting pin');
    }
}
