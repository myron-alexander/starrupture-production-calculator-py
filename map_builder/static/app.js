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
const editTeleporter = document.getElementById('editTeleporter');
const editDescription = document.getElementById('editDescription');

// Resource Node Modal Elements
const resourceNodeModal = document.getElementById('resourceNodeModal');
const resourceNodeModalTitle = document.getElementById('resourceNodeModalTitle');
const resourceNodeId = document.getElementById('resourceNodeId');
const resourceItem = document.getElementById('resourceItem');
const resourceRate = document.getElementById('resourceRate');
const resourceVariant = document.getElementById('resourceVariant');
const resourceCoreId = document.getElementById('resourceCoreId');
const saveResourceNodeBtn = document.getElementById('saveResourceNodeBtn');
const deleteResourceNodeBtn = document.getElementById('deleteResourceNodeBtn');

// Core Modal Elements
const coreModal = document.getElementById('coreModal');
const coreModalTitle = document.getElementById('coreModalTitle');
const coreId = document.getElementById('coreId');
const coreLevel = document.getElementById('coreLevel');
const saveCoreBtn = document.getElementById('saveCoreBtn');
const deleteCoreBtn = document.getElementById('deleteCoreBtn');

// Factory Modal Elements
const factoryModal = document.getElementById('factoryModal');
const factoryModalTitle = document.getElementById('factoryModalTitle');
const factoryId = document.getElementById('factoryId');
const factoryPurpose = document.getElementById('factoryPurpose');
const factoryDefaultCore = document.getElementById('factoryDefaultCore');
const saveFactoryBtn = document.getElementById('saveFactoryBtn');
const deleteFactoryBtn = document.getElementById('deleteFactoryBtn');

// Receiver Modal Elements
const receiverModal = document.getElementById('receiverModal');
const receiverModalTitle = document.getElementById('receiverModalTitle');
const receiverId = document.getElementById('receiverId');
const receiverSiteId = document.getElementById('receiverSiteId');
const receiverFactoryId = document.getElementById('receiverFactoryId');
const receiverDispatcherId = document.getElementById('receiverDispatcherId');
const receiverBuildingId = document.getElementById('receiverBuildingId');
const saveReceiverBtn = document.getElementById('saveReceiverBtn');
const deleteReceiverBtn = document.getElementById('deleteReceiverBtn');

// Dispatcher Modal Elements
const dispatcherModal = document.getElementById('dispatcherModal');
const dispatcherModalTitle = document.getElementById('dispatcherModalTitle');
const dispatcherId = document.getElementById('dispatcherId');
const dispatchedItem = document.getElementById('dispatchedItem');
const dispatcherOutputRate = document.getElementById('dispatcherOutputRate');
const dispatcherInputRate = document.getElementById('dispatcherInputRate');
const dispatcherFromIds = document.getElementById('dispatcherFromIds');
const dispatcherBuildingId = document.getElementById('dispatcherBuildingId');
const saveDispatcherBtn = document.getElementById('saveDispatcherBtn');
const deleteDispatcherBtn = document.getElementById('deleteDispatcherBtn');

let pins = {};
let selectedPinId = null;
let editingResourceNodeId = null;
let editingCoreId = null;
let editingFactoryId = null;
let selectedFactoryId = null;
let editingReceiverId = null;
let editingDispatcherId = null;

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
    
    // Site Modal controls
    closeBtn.addEventListener('click', closeEditModal);
    savePinBtn.addEventListener('click', handleSavePin);
    deletePinBtn.addEventListener('click', handleDeletePin);
    
    // Resource Node Modal controls
    document.querySelectorAll('[data-modal="resourceNodeModal"]').forEach(el => {
        el.addEventListener('click', closeResourceNodeModal);
    });
    saveResourceNodeBtn.addEventListener('click', handleSaveResourceNode);
    deleteResourceNodeBtn.addEventListener('click', handleDeleteResourceNode);
    
    // Core Modal controls
    document.querySelectorAll('[data-modal="coreModal"]').forEach(el => {
        el.addEventListener('click', closeCoreModal);
    });
    saveCoreBtn.addEventListener('click', handleSaveCore);
    deleteCoreBtn.addEventListener('click', handleDeleteCore);
    
    // Factory Modal controls
    document.querySelectorAll('[data-modal="factoryModal"]').forEach(el => {
        el.addEventListener('click', closeFactoryModal);
    });
    saveFactoryBtn.addEventListener('click', handleSaveFactory);
    deleteFactoryBtn.addEventListener('click', handleDeleteFactory);
    
    // Receiver Modal controls
    document.querySelectorAll('[data-modal="receiverModal"]').forEach(el => {
        el.addEventListener('click', closeReceiverModal);
    });
    saveReceiverBtn.addEventListener('click', handleSaveReceiver);
    deleteReceiverBtn.addEventListener('click', handleDeleteReceiver);
    
    // Dispatcher Modal controls
    document.querySelectorAll('[data-modal="dispatcherModal"]').forEach(el => {
        el.addEventListener('click', closeDispatcherModal);
    });
    saveDispatcherBtn.addEventListener('click', handleSaveDispatcher);
    deleteDispatcherBtn.addEventListener('click', handleDeleteDispatcher);
    
    window.addEventListener('click', (event) => {
        if (event.target === editModal) {
            closeEditModal();
        }
        if (event.target === resourceNodeModal) {
            closeResourceNodeModal();
        }
        if (event.target === coreModal) {
            closeCoreModal();
        }
        if (event.target === factoryModal) {
            closeFactoryModal();
        }
        if (event.target === receiverModal) {
            closeReceiverModal();
        }
        if (event.target === dispatcherModal) {
            closeDispatcherModal();
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
        pinsList.innerHTML = '<div class="pin-item empty">No sites yet</div>';
        return;
    }
    
    Object.entries(pins).forEach(([id, pin], index) => {
        const pinItem = document.createElement('div');
        pinItem.className = 'pin-item';
        
        // Create header with name and expand/collapse toggle
        const header = document.createElement('div');
        header.className = 'pin-item-header';
        header.innerHTML = `
            <div>
                <div class="pin-item-name">${index + 1}. ${pin.name}</div>
                <div class="pin-item-coords">Grid: (${pin.x}, ${pin.y})</div>
            </div>
            <span class="pin-item-toggle" data-pin-id="${id}">▼</span>
        `;
        
        // Create details section (initially hidden)
        const details = document.createElement('div');
        details.className = 'pin-item-details';
        details.id = `details-${id}`;
        
        // Add site details
        let detailsHTML = '';
        if (pin.teleporter) {
            detailsHTML += `
                <div class="pin-detail-row">
                    <div class="pin-detail-label">Teleporter:</div>
                    <div class="pin-detail-value">${pin.teleporter}</div>
                </div>
            `;
        }
        if (pin.description) {
            detailsHTML += `
                <div class="pin-detail-row">
                    <div class="pin-detail-label">Description:</div>
                    <div class="pin-detail-value">${pin.description}</div>
                </div>
            `;
        }
        
        // Add Resource Nodes section
        detailsHTML += renderTreeSection('Resource Nodes', pin.resource_nodes || {});
        
        // Add Cores section
        detailsHTML += renderTreeSection('Cores', pin.cores || {});
        
        // Add Factories section
        detailsHTML += renderTreeSection('Factories', pin.factories || {});
        
        details.innerHTML = detailsHTML;
        
        pinItem.appendChild(header);
        pinItem.appendChild(details);
        
        // Add toggle functionality
        const toggle = header.querySelector('.pin-item-toggle');
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDetails(id);
        });
        
        // Click on header (not toggle) opens edit modal
        header.addEventListener('click', (e) => {
            if (!e.target.classList.contains('pin-item-toggle')) {
                openEditModal(id);
            }
        });
        
        // Add event listeners for tree blocks
        details.addEventListener('click', (e) => {
            const addBtn = e.target.closest('.add-button');
            const treeBlock = e.target.closest('.tree-block:not(.add-button)');
            
            if (addBtn) {
                const section = addBtn.closest('.tree-section');
                const sectionHeader = section.querySelector('.tree-section-header').textContent;
                const factoryId = addBtn.dataset.factoryId;
                
                if (sectionHeader.includes('Resource Nodes')) {
                    openAddResourceNodeModal(id);
                } else if (sectionHeader.includes('Cores')) {
                    openAddCoreModal(id);
                } else if (sectionHeader.includes('Factories')) {
                    openAddFactoryModal(id);
                } else if (sectionHeader.includes('Receivers') && factoryId) {
                    openAddReceiverModal(id, factoryId);
                } else if (sectionHeader.includes('Dispatchers') && factoryId) {
                    openAddDispatcherModal(id, factoryId);
                }
            } else if (treeBlock) {
                const itemId = treeBlock.dataset.itemId;
                const factoryId = treeBlock.dataset.factoryId;
                const section = treeBlock.closest('.tree-section');
                const sectionHeader = section.querySelector('.tree-section-header').textContent;
                
                if (sectionHeader.includes('Resource Nodes')) {
                    openEditResourceNodeModal(id, itemId);
                } else if (sectionHeader.includes('Cores')) {
                    openEditCoreModal(id, itemId);
                } else if (sectionHeader.includes('Factories')) {
                    openEditFactoryModal(id, itemId);
                } else if (sectionHeader.includes('Receivers') && factoryId) {
                    openEditReceiverModal(id, factoryId, itemId);
                } else if (sectionHeader.includes('Dispatchers') && factoryId) {
                    openEditDispatcherModal(id, factoryId, itemId);
                }
            }
        });
        
        pinsList.appendChild(pinItem);
    });
}

function renderTreeSection(title, items) {
    const itemIds = Object.keys(items).sort(); // Sort alphabetically
    let html = `
        <div class="tree-section">
            <div class="tree-section-header">${title} (${itemIds.length})</div>
    `;
    
    if (itemIds.length === 0) {
        html += `
            <div class="tree-block add-button">
                + Add ${title.slice(0, -1)}
            </div>
        `;
    } else {
        itemIds.forEach(itemId => {
            const item = items[itemId];
            html += `
                <div class="tree-block" data-item-id="${itemId}">
                    <div class="tree-block-label">${itemId}</div>
                    ${renderItemDetails(title, item, itemId)}
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button">
                + Add ${title.slice(0, -1)}
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function renderReceiversTree(receivers, factoryId) {
    const receiverIds = Object.keys(receivers).sort();
    let html = `
        <div class="tree-section" style="margin-left: 20px; margin-top: 10px;">
            <div class="tree-section-header">Receivers (${receiverIds.length})</div>
    `;
    
    if (receiverIds.length === 0) {
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Receiver
            </div>
        `;
    } else {
        receiverIds.forEach(receiverId => {
            const receiver = receivers[receiverId];
            html += `
                <div class="tree-block" data-item-id="${receiverId}" data-factory-id="${factoryId}">
                    <div class="tree-block-label">${receiverId}</div>
                    ${renderItemDetails('Receivers', receiver)}
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Receiver
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function renderDispatchersTree(dispatchers, factoryId) {
    const dispatcherIds = Object.keys(dispatchers).sort();
    let html = `
        <div class="tree-section" style="margin-left: 20px; margin-top: 10px;">
            <div class="tree-section-header">Dispatchers (${dispatcherIds.length})</div>
    `;
    
    if (dispatcherIds.length === 0) {
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Dispatcher
            </div>
        `;
    } else {
        dispatcherIds.forEach(dispatcherId => {
            const dispatcher = dispatchers[dispatcherId];
            html += `
                <div class="tree-block" data-item-id="${dispatcherId}" data-factory-id="${factoryId}">
                    <div class="tree-block-label">${dispatcherId}</div>
                    ${renderItemDetails('Dispatchers', dispatcher)}
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Dispatcher
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function renderItemDetails(sectionType, item, itemId = null) {
    if (sectionType === 'Resource Nodes') {
        return `
            <div class="tree-block-value">${item.resource_item || 'Unknown'} - ${item.rate_ipm || 0} ipm</div>
            <div class="tree-block-value">${item.variant || 'normal'}</div>
        `;
    } else if (sectionType === 'Cores') {
        return `
            <div class="tree-block-value">Level: ${item.core_level || 0}</div>
        `;
    } else if (sectionType === 'Factories') {
        let html = `
            <div class="tree-block-value">${item.purpose || 'No purpose set'}</div>
        `;
        // Add receivers and dispatchers as children of factory
        if (item.receivers && Object.keys(item.receivers).length > 0) {
            html += renderReceiversTree(item.receivers, itemId);
        } else {
            html += renderReceiversTree({}, itemId);
        }
        if (item.dispatchers && Object.keys(item.dispatchers).length > 0) {
            html += renderDispatchersTree(item.dispatchers, itemId);
        } else {
            html += renderDispatchersTree({}, itemId);
        }
        return html;
    } else if (sectionType === 'Receivers') {
        return `
            <div class="tree-block-value">From: ${item.site_id || '?'}/${item.factory_id || '?'}/${item.dispatcher_id || '?'}</div>
            ${item.building_id ? `<div class="tree-block-value">Building: ${item.building_id}</div>` : ''}
        `;
    } else if (sectionType === 'Dispatchers') {
        const fromIds = Array.isArray(item.from_ids) ? item.from_ids.join(', ') : item.from_ids || 'None';
        return `
            <div class="tree-block-value">${item.dipatched_item || item.dispatched_item || 'Unknown item'}</div>
            <div class="tree-block-value">Out: ${item.output_rate_limit_ipm || 0} ipm, In: ${item.input_rate_limit_ipm || 0} ipm</div>
            <div class="tree-block-value">From: ${fromIds}</div>
            ${item.building_id ? `<div class="tree-block-value">Building: ${item.building_id}</div>` : ''}
        `;
    }
    return '';
}

function toggleDetails(pinId) {
    const details = document.getElementById(`details-${pinId}`);
    const toggle = document.querySelector(`[data-pin-id="${pinId}"]`);
    
    if (details.classList.contains('expanded')) {
        details.classList.remove('expanded');
        toggle.textContent = '▼';
    } else {
        details.classList.add('expanded');
        toggle.textContent = '▲';
    }
}

function openEditModal(pinId) {
    selectedPinId = pinId;
    const pin = pins[pinId];
    
    editPinName.value = pin.name;
    editPinX.value = pin.x;
    editPinY.value = pin.y;
    editTeleporter.value = pin.teleporter || '';
    editDescription.value = pin.description || '';
    
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
    const teleporter = editTeleporter.value.trim();
    const description = editDescription.value.trim();
    
    if (!name) {
        alert('Please enter a site name');
        return;
    }
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, x, y, teleporter, description })
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

// Resource Node Modal Functions
function populateResourceNodeCoreOptions(pinId, selectedCoreId = '') {
    const cores = (pins[pinId] && pins[pinId].cores) ? pins[pinId].cores : {};
    const coreIds = Object.keys(cores).sort();

    resourceCoreId.innerHTML = '';
    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '';
    resourceCoreId.appendChild(emptyOption);

    coreIds.forEach(coreId => {
        const option = document.createElement('option');
        option.value = coreId;
        option.textContent = coreId;
        resourceCoreId.appendChild(option);
    });

    if (selectedCoreId && coreIds.includes(selectedCoreId)) {
        resourceCoreId.value = selectedCoreId;
    } else {
        resourceCoreId.value = '';
    }
}

function openAddResourceNodeModal(pinId) {
    selectedPinId = pinId;
    editingResourceNodeId = null;
    resourceNodeModalTitle.textContent = 'Add Resource Node';
    resourceNodeId.value = '';
    resourceNodeId.disabled = false;
    if (resourceItem.options.length > 0) {
        resourceItem.value = resourceItem.options[0].value;
    }
    resourceRate.value = '60';
    resourceVariant.value = 'normal';
    populateResourceNodeCoreOptions(pinId);
    deleteResourceNodeBtn.style.display = 'none';
    resourceNodeModal.classList.add('show');
}

function openEditResourceNodeModal(pinId, nodeId) {
    selectedPinId = pinId;
    editingResourceNodeId = nodeId;
    const node = pins[pinId].resource_nodes[nodeId];
    
    resourceNodeModalTitle.textContent = 'Edit Resource Node';
    resourceNodeId.value = nodeId;
    resourceNodeId.disabled = true;
    resourceItem.value = node.resource_item || 'calcium ore';
    resourceRate.value = node.rate_ipm || 60;
    resourceVariant.value = node.variant || 'normal';
    populateResourceNodeCoreOptions(pinId, node.core_id || '');
    deleteResourceNodeBtn.style.display = 'block';
    resourceNodeModal.classList.add('show');
}

function closeResourceNodeModal() {
    resourceNodeModal.classList.remove('show');
    editingResourceNodeId = null;
}

async function handleSaveResourceNode() {
    if (!selectedPinId) return;
    
    const nodeId = resourceNodeId.value.trim();
    if (!nodeId) {
        alert('Please enter a resource ID');
        return;
    }
    
    // Check for duplicate ID when adding new
    if (!editingResourceNodeId && pins[selectedPinId].resource_nodes && pins[selectedPinId].resource_nodes[nodeId]) {
        alert('A resource node with this ID already exists');
        return;
    }
    
    // Validate core ID if specified
    const coreIds = pins[selectedPinId] && pins[selectedPinId].cores
        ? Object.keys(pins[selectedPinId].cores)
        : [];
    const selectedCoreId = resourceCoreId.value.trim();
    if (selectedCoreId && !coreIds.includes(selectedCoreId)) {
        alert('Please select a valid core ID');
        return;
    }
    
    const nodeData = {
        resource_item: resourceItem.value,
        rate_ipm: parseInt(resourceRate.value),
        variant: resourceVariant.value,
        core_id: selectedCoreId
    };
    
    if (!pins[selectedPinId].resource_nodes) {
        pins[selectedPinId].resource_nodes = {};
    }
    
    // If editing and ID changed, delete old entry
    if (editingResourceNodeId && editingResourceNodeId !== nodeId) {
        delete pins[selectedPinId].resource_nodes[editingResourceNodeId];
    }
    
    pins[selectedPinId].resource_nodes[nodeId] = nodeData;
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_nodes: pins[selectedPinId].resource_nodes })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeResourceNodeModal();
        }
    } catch (error) {
        console.error('Error saving resource node:', error);
        alert('Error saving resource node');
    }
}

async function handleDeleteResourceNode() {
    if (!selectedPinId || !editingResourceNodeId) return;
    
    delete pins[selectedPinId].resource_nodes[editingResourceNodeId];
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_nodes: pins[selectedPinId].resource_nodes })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeResourceNodeModal();
        }
    } catch (error) {
        console.error('Error deleting resource node:', error);
        alert('Error deleting resource node');
    }
}

// Core Modal Functions
function openAddCoreModal(pinId) {
    selectedPinId = pinId;
    editingCoreId = null;
    coreModalTitle.textContent = 'Add Core';
    coreId.value = '';
    coreId.disabled = false;
    coreLevel.value = '0';
    deleteCoreBtn.style.display = 'none';
    coreModal.classList.add('show');
}

function openEditCoreModal(pinId, corId) {
    selectedPinId = pinId;
    editingCoreId = corId;
    const core = pins[pinId].cores[corId];
    
    coreModalTitle.textContent = 'Edit Core';
    coreId.value = corId;
    coreId.disabled = true;
    coreLevel.value = core.core_level || 0;
    deleteCoreBtn.style.display = 'block';
    coreModal.classList.add('show');
}

function closeCoreModal() {
    coreModal.classList.remove('show');
    editingCoreId = null;
}

async function handleSaveCore() {
    if (!selectedPinId) return;
    
    const corId = coreId.value.trim();
    if (!corId) {
        alert('Please enter a core ID');
        return;
    }
    
    // Check for duplicate ID when adding new
    if (!editingCoreId && pins[selectedPinId].cores && pins[selectedPinId].cores[corId]) {
        alert('A core with this ID already exists');
        return;
    }
    
    const coreData = {
        core_level: parseInt(coreLevel.value),
        non_production_buildings: []
    };
    
    if (!pins[selectedPinId].cores) {
        pins[selectedPinId].cores = {};
    }
    
    // If editing and ID changed, delete old entry
    if (editingCoreId && editingCoreId !== corId) {
        delete pins[selectedPinId].cores[editingCoreId];
    }
    
    pins[selectedPinId].cores[corId] = coreData;
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cores: pins[selectedPinId].cores })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeCoreModal();
        }
    } catch (error) {
        console.error('Error saving core:', error);
        alert('Error saving core');
    }
}

async function handleDeleteCore() {
    if (!selectedPinId || !editingCoreId) return;
    
    delete pins[selectedPinId].cores[editingCoreId];
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cores: pins[selectedPinId].cores })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeCoreModal();
        }
    } catch (error) {
        console.error('Error deleting core:', error);
        alert('Error deleting core');
    }
}

// Factory Modal Functions
function populateFactoryCoreOptions(pinId, selectedCoreId = '') {
    const cores = (pins[pinId] && pins[pinId].cores) ? pins[pinId].cores : {};
    const coreIds = Object.keys(cores).sort();

    factoryDefaultCore.innerHTML = '';

    coreIds.forEach(coreId => {
        const option = document.createElement('option');
        option.value = coreId;
        option.textContent = coreId;
        factoryDefaultCore.appendChild(option);
    });

    factoryDefaultCore.disabled = coreIds.length === 0;

    if (selectedCoreId && coreIds.includes(selectedCoreId)) {
        factoryDefaultCore.value = selectedCoreId;
    } else if (coreIds.length > 0) {
        factoryDefaultCore.value = coreIds[0];
    }
}

function openAddFactoryModal(pinId) {
    selectedPinId = pinId;
    editingFactoryId = null;
    factoryModalTitle.textContent = 'Add Factory';
    factoryId.value = '';
    factoryId.disabled = false;
    factoryPurpose.value = '';
    populateFactoryCoreOptions(pinId);
    deleteFactoryBtn.style.display = 'none';
    factoryModal.classList.add('show');
}

function openEditFactoryModal(pinId, facId) {
    selectedPinId = pinId;
    editingFactoryId = facId;
    const factory = pins[pinId].factories[facId];
    
    factoryModalTitle.textContent = 'Edit Factory';
    factoryId.value = facId;
    factoryId.disabled = true;
    factoryPurpose.value = factory.purpose || '';
    populateFactoryCoreOptions(pinId, factory.default_core || '');
    deleteFactoryBtn.style.display = 'block';
    factoryModal.classList.add('show');
}

function closeFactoryModal() {
    factoryModal.classList.remove('show');
    editingFactoryId = null;
}

async function handleSaveFactory() {
    if (!selectedPinId) return;
    
    const facId = factoryId.value.trim();
    if (!facId) {
        alert('Please enter a factory ID');
        return;
    }
    
    // Check for duplicate ID when adding new
    if (!editingFactoryId && pins[selectedPinId].factories && pins[selectedPinId].factories[facId]) {
        alert('A factory with this ID already exists');
        return;
    }
    
    const coreIds = pins[selectedPinId] && pins[selectedPinId].cores
        ? Object.keys(pins[selectedPinId].cores)
        : [];
    const selectedCoreId = factoryDefaultCore.value.trim();
    if (!selectedCoreId) {
        alert('Please select a core ID');
        return;
    }
    if (!coreIds.includes(selectedCoreId)) {
        alert('Please select a valid core ID');
        return;
    }

    const factoryData = {
        purpose: factoryPurpose.value.trim(),
        default_core: selectedCoreId,
        machines: {}
    };
    
    if (!pins[selectedPinId].factories) {
        pins[selectedPinId].factories = {};
    }
    
    // If editing and ID changed, delete old entry
    if (editingFactoryId && editingFactoryId !== facId) {
        delete pins[selectedPinId].factories[editingFactoryId];
    }
    
    pins[selectedPinId].factories[facId] = factoryData;
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ factories: pins[selectedPinId].factories })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeFactoryModal();
        }
    } catch (error) {
        console.error('Error saving factory:', error);
        alert('Error saving factory');
    }
}

async function handleDeleteFactory() {
    if (!selectedPinId || !editingFactoryId) return;
    
    delete pins[selectedPinId].factories[editingFactoryId];
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ factories: pins[selectedPinId].factories })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeFactoryModal();
        }
    } catch (error) {
        console.error('Error deleting factory:', error);
        alert('Error deleting factory');
    }
}

// Receiver Modal Functions
function openAddReceiverModal(pinId, factoryId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingReceiverId = null;
    receiverModalTitle.textContent = 'Add Receiver';
    receiverId.value = '';
    receiverId.disabled = false;
    receiverSiteId.value = '';
    receiverFactoryId.value = '';
    receiverDispatcherId.value = '';
    receiverBuildingId.value = '';
    deleteReceiverBtn.style.display = 'none';
    receiverModal.classList.add('show');
}

function openEditReceiverModal(pinId, factoryId, recId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingReceiverId = recId;
    const receiver = pins[pinId].factories[factoryId].receivers[recId];
    
    receiverModalTitle.textContent = 'Edit Receiver';
    receiverId.value = recId;
    receiverId.disabled = true;
    receiverSiteId.value = receiver.site_id || '';
    receiverFactoryId.value = receiver.factory_id || '';
    receiverDispatcherId.value = receiver.dispatcher_id || '';
    receiverBuildingId.value = receiver.building_id || '';
    deleteReceiverBtn.style.display = 'block';
    receiverModal.classList.add('show');
}

function closeReceiverModal() {
    receiverModal.classList.remove('show');
    editingReceiverId = null;
    selectedFactoryId = null;
}

async function handleSaveReceiver() {
    if (!selectedPinId || !selectedFactoryId) return;
    
    const recId = receiverId.value.trim();
    if (!recId) {
        alert('Please enter a receiver ID');
        return;
    }
    
    // Initialize factory.receivers if needed
    if (!pins[selectedPinId].factories[selectedFactoryId].receivers) {
        pins[selectedPinId].factories[selectedFactoryId].receivers = {};
    }
    
    // Check for duplicate ID when adding new
    if (!editingReceiverId && pins[selectedPinId].factories[selectedFactoryId].receivers[recId]) {
        alert('A receiver with this ID already exists');
        return;
    }
    
    const receiverData = {
        site_id: receiverSiteId.value.trim(),
        factory_id: receiverFactoryId.value.trim(),
        dispatcher_id: receiverDispatcherId.value.trim(),
        building_id: receiverBuildingId.value.trim()
    };
    
    // If editing and ID changed, delete old entry
    if (editingReceiverId && editingReceiverId !== recId) {
        delete pins[selectedPinId].factories[selectedFactoryId].receivers[editingReceiverId];
    }
    
    pins[selectedPinId].factories[selectedFactoryId].receivers[recId] = receiverData;
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ factories: pins[selectedPinId].factories })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeReceiverModal();
        }
    } catch (error) {
        console.error('Error saving receiver:', error);
        alert('Error saving receiver');
    }
}

async function handleDeleteReceiver() {
    if (!selectedPinId || !selectedFactoryId || !editingReceiverId) return;
    
    delete pins[selectedPinId].factories[selectedFactoryId].receivers[editingReceiverId];
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ factories: pins[selectedPinId].factories })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeReceiverModal();
        }
    } catch (error) {
        console.error('Error deleting receiver:', error);
        alert('Error deleting receiver');
    }
}

// Dispatcher Modal Functions
function openAddDispatcherModal(pinId, factoryId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingDispatcherId = null;
    dispatcherModalTitle.textContent = 'Add Dispatcher';
    dispatcherId.value = '';
    dispatcherId.disabled = false;
    dispatchedItem.value = '';
    dispatcherOutputRate.value = '100';
    dispatcherInputRate.value = '100';
    dispatcherFromIds.value = '';
    dispatcherBuildingId.value = '';
    deleteDispatcherBtn.style.display = 'none';
    dispatcherModal.classList.add('show');
}

function openEditDispatcherModal(pinId, factoryId, dispId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingDispatcherId = dispId;
    const dispatcher = pins[pinId].factories[factoryId].dispatchers[dispId];
    
    dispatcherModalTitle.textContent = 'Edit Dispatcher';
    dispatcherId.value = dispId;
    dispatcherId.disabled = true;
    dispatchedItem.value = dispatcher.dipatched_item || dispatcher.dispatched_item || '';
    dispatcherOutputRate.value = dispatcher.output_rate_limit_ipm || 100;
    dispatcherInputRate.value = dispatcher.input_rate_limit_ipm || 100;
    const fromIds = Array.isArray(dispatcher.from_ids) ? dispatcher.from_ids.join(', ') : dispatcher.from_ids || '';
    dispatcherFromIds.value = fromIds;
    dispatcherBuildingId.value = dispatcher.building_id || '';
    deleteDispatcherBtn.style.display = 'block';
    dispatcherModal.classList.add('show');
}

function closeDispatcherModal() {
    dispatcherModal.classList.remove('show');
    editingDispatcherId = null;
    selectedFactoryId = null;
}

async function handleSaveDispatcher() {
    if (!selectedPinId || !selectedFactoryId) return;
    
    const dispId = dispatcherId.value.trim();
    if (!dispId) {
        alert('Please enter a dispatcher ID');
        return;
    }
    
    if (!dispatchedItem.value.trim()) {
        alert('Please select a dispatched item');
        return;
    }
    
    // Initialize factory.dispatchers if needed
    if (!pins[selectedPinId].factories[selectedFactoryId].dispatchers) {
        pins[selectedPinId].factories[selectedFactoryId].dispatchers = {};
    }
    
    // Check for duplicate ID when adding new
    if (!editingDispatcherId && pins[selectedPinId].factories[selectedFactoryId].dispatchers[dispId]) {
        alert('A dispatcher with this ID already exists');
        return;
    }
    
    // Parse from_ids from textarea (comma-separated)
    const fromIdsText = dispatcherFromIds.value.trim();
    const fromIds = fromIdsText ? fromIdsText.split(',').map(id => id.trim()).filter(id => id) : [];
    
    const dispatcherData = {
        dipatched_item: dispatchedItem.value.trim(),
        output_rate_limit_ipm: parseInt(dispatcherOutputRate.value),
        input_rate_limit_ipm: parseInt(dispatcherInputRate.value),
        from_ids: fromIds,
        building_id: dispatcherBuildingId.value.trim()
    };
    
    // If editing and ID changed, delete old entry
    if (editingDispatcherId && editingDispatcherId !== dispId) {
        delete pins[selectedPinId].factories[selectedFactoryId].dispatchers[editingDispatcherId];
    }
    
    pins[selectedPinId].factories[selectedFactoryId].dispatchers[dispId] = dispatcherData;
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ factories: pins[selectedPinId].factories })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeDispatcherModal();
        }
    } catch (error) {
        console.error('Error saving dispatcher:', error);
        alert('Error saving dispatcher');
    }
}

async function handleDeleteDispatcher() {
    if (!selectedPinId || !selectedFactoryId || !editingDispatcherId) return;
    
    delete pins[selectedPinId].factories[selectedFactoryId].dispatchers[editingDispatcherId];
    
    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ factories: pins[selectedPinId].factories })
        });
        
        if (response.ok) {
            const updatedPin = await response.json();
            pins[selectedPinId] = updatedPin;
            renderPins();
            renderPinsList();
            closeDispatcherModal();
        }
    } catch (error) {
        console.error('Error deleting dispatcher:', error);
        alert('Error deleting dispatcher');
    }
}
