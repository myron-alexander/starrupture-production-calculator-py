// DOM Elements
const mapContainer = document.getElementById('mapContainer');
const mapImage = document.getElementById('mapImage');
const pinsOverlay = document.getElementById('pinsOverlay');
const coordXDisplay = document.getElementById('coordX');
const coordYDisplay = document.getElementById('coordY');
const pinsList = document.getElementById('pinsList');

// Add Pin Modal Elements
const addPinModal = document.getElementById('addPinModal');
const addPinName = document.getElementById('addPinName');
const addPinX = document.getElementById('addPinX');
const addPinY = document.getElementById('addPinY');
const saveAddPinBtn = document.getElementById('saveAddPinBtn');

// Edit Pin Modal Elements
const editModal = document.getElementById('editModal');
const savePinBtn = document.getElementById('savePinBtn');
const deletePinBtn = document.getElementById('deletePinBtn');
const editPinName = document.getElementById('editPinName');
const editPinX = document.getElementById('editPinX');
const editPinY = document.getElementById('editPinY');
const editTeleporter = document.getElementById('editTeleporter');
const editDescription = document.getElementById('editDescription');

// Resource Node Modal Elements
const resourceNodeModal = document.getElementById('resourceNodeModal');
const selectResourceModal = document.getElementById('selectResourceModal');
const resourceNodeModalTitle = document.getElementById('resourceNodeModalTitle');
const resourceNodeId = document.getElementById('resourceNodeId');
const selectResourceBtn = document.getElementById('selectResourceBtn');
const resourceItemLabel = document.getElementById('resourceItemLabel');
const resourceVariantLabel = document.getElementById('resourceVariantLabel');
const resourceRateLabel = document.getElementById('resourceRateLabel');
const resourceBuildingLabel = document.getElementById('resourceBuildingLabel');
const resourceNodeCoreId = document.getElementById('resourceNodeCoreId');
const saveResourceNodeBtn = document.getElementById('saveResourceNodeBtn');
const deleteResourceNodeBtn = document.getElementById('deleteResourceNodeBtn');
const resourceSelectionTable = document.getElementById('resourceSelectionTable');

// Store selected resource data
let selectedResourceData = null;

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
const receiverCoreGroup = document.getElementById('receiverCoreGroup');
const receiverCoreId = document.getElementById('receiverCoreId');
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
const dispatcherCoreGroup = document.getElementById('dispatcherCoreGroup');
const dispatcherCoreId = document.getElementById('dispatcherCoreId');
const saveDispatcherBtn = document.getElementById('saveDispatcherBtn');
const deleteDispatcherBtn = document.getElementById('deleteDispatcherBtn');

// Crafter Modal Elements
const crafterModal = document.getElementById('crafterModal');
const crafterModalTitle = document.getElementById('crafterModalTitle');
const crafterId = document.getElementById('crafterId');
const crafterItem = document.getElementById('crafterItem');
const crafterInputsContainer = document.getElementById('crafterInputsContainer');
const crafterCoreId = document.getElementById('crafterCoreId');
const saveCrafterBtn = document.getElementById('saveCrafterBtn');
const deleteCrafterBtn = document.getElementById('deleteCrafterBtn');

// Storage Modal Elements
const storageModal = document.getElementById('storageModal');
const storageModalTitle = document.getElementById('storageModalTitle');
const storageId = document.getElementById('storageId');
const storageBuildingId = document.getElementById('storageBuildingId');
const storageNumStacks = document.getElementById('storageNumStacks');
const storageStoredItem = document.getElementById('storageStoredItem');
const storageCoreId = document.getElementById('storageCoreId');
const storageInputsContainer = document.getElementById('storageInputsContainer');
const addStorageInputBtn = document.getElementById('addStorageInputBtn');
const saveStorageBtn = document.getElementById('saveStorageBtn');
const deleteStorageBtn = document.getElementById('deleteStorageBtn');

// Non-Production Building Modal Elements
const nonProdBuildingModal = document.getElementById('nonProdBuildingModal');
const nonProdBuildingModalTitle = document.getElementById('nonProdBuildingModalTitle');
const nonProdBuildingId = document.getElementById('nonProdBuildingId');
const nonProdBuildingCount = document.getElementById('nonProdBuildingCount');
const saveNonProdBuildingBtn = document.getElementById('saveNonProdBuildingBtn');
const deleteNonProdBuildingBtn = document.getElementById('deleteNonProdBuildingBtn');

let pins = {};
let selectedPinId = null;
let editingResourceNodeId = null;
let editingCoreId = null;
let editingFactoryId = null;
let selectedFactoryId = null;
let editingReceiverId = null;
let editingDispatcherId = null;
let selectedCoreId = null;
let editingBuildingIndex = null;
let editingCrafterId = null;
let editingStorageId = null;

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
    
    // Add Pin Modal controls
    document.querySelectorAll('[data-modal="addPinModal"]').forEach(el => {
        el.addEventListener('click', closeAddPinModal);
    });
    saveAddPinBtn.addEventListener('click', handleAddPin);
    
    // Edit Site Modal controls
    document.querySelectorAll('[data-modal="editModal"]').forEach(el => {
        el.addEventListener('click', closeEditModal);
    });
    savePinBtn.addEventListener('click', handleSavePin);
    deletePinBtn.addEventListener('click', handleDeletePin);
    
    // Resource Node Modal controls
    document.querySelectorAll('[data-modal="resourceNodeModal"]').forEach(el => {
        el.addEventListener('click', closeResourceNodeModal);
    });
    document.querySelectorAll('[data-modal="selectResourceModal"]').forEach(el => {
        el.addEventListener('click', closeSelectResourceModal);
    });
    selectResourceBtn.addEventListener('click', openSelectResourceModal);
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
    receiverBuildingId.addEventListener('change', handleReceiverBuildingChange);
    saveReceiverBtn.addEventListener('click', handleSaveReceiver);
    deleteReceiverBtn.addEventListener('click', handleDeleteReceiver);
    
    // Dispatcher Modal controls
    document.querySelectorAll('[data-modal="dispatcherModal"]').forEach(el => {
        el.addEventListener('click', closeDispatcherModal);
    });
    dispatcherBuildingId.addEventListener('change', handleDispatcherBuildingChange);
    saveDispatcherBtn.addEventListener('click', handleSaveDispatcher);
    deleteDispatcherBtn.addEventListener('click', handleDeleteDispatcher);

    // Crafter Modal controls
    document.querySelectorAll('[data-modal="crafterModal"]').forEach(el => {
        el.addEventListener('click', closeCrafterModal);
    });
    crafterItem.addEventListener('change', handleCrafterItemChange);
    saveCrafterBtn.addEventListener('click', handleSaveCrafter);
    deleteCrafterBtn.addEventListener('click', handleDeleteCrafter);
    
    // Storage Modal controls
    document.querySelectorAll('[data-modal="storageModal"]').forEach(el => {
        el.addEventListener('click', closeStorageModal);
    });
    addStorageInputBtn.addEventListener('click', () => {
        addStorageInputRow();
    });
    saveStorageBtn.addEventListener('click', handleSaveStorage);
    deleteStorageBtn.addEventListener('click', handleDeleteStorage);
    
    // Non-Production Building Modal controls
    document.querySelectorAll('[data-modal="nonProdBuildingModal"]').forEach(el => {
        el.addEventListener('click', closeNonProdBuildingModal);
    });
    saveNonProdBuildingBtn.addEventListener('click', handleSaveNonProdBuilding);
    deleteNonProdBuildingBtn.addEventListener('click', handleDeleteNonProdBuilding);
    
    window.addEventListener('click', (event) => {
        if (event.target === addPinModal) {
            closeAddPinModal();
        }
        if (event.target === editModal) {
            console.log("close edit modal button pressed.")
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
        if (event.target === crafterModal) {
            closeCrafterModal();
        }
        if (event.target === storageModal) {
            closeStorageModal();
        }
        if (event.target === nonProdBuildingModal) {
            closeNonProdBuildingModal();
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
    
    // Show add pin modal with coordinates pre-filled
    openAddPinModal(gridX, gridY);
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
    const name = addPinName.value.trim();
    let x = parseInt(addPinX.value);
    let y = parseInt(addPinY.value);
    
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
            
            // Close modal
            closeAddPinModal();
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
                const coreId = addBtn.dataset.coreId;
                
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
                } else if (sectionHeader.includes('Crafters') && factoryId) {
                    openAddCrafterModal(id, factoryId);
                } else if (sectionHeader.includes('Storage') && factoryId) {
                    openAddStorageModal(id, factoryId);
                } else if (sectionHeader.includes('Non-Production Buildings') && coreId) {
                    openAddNonProdBuildingModal(id, coreId);
                }
            } else if (treeBlock) {
                const itemId = treeBlock.dataset.itemId;
                const factoryId = treeBlock.dataset.factoryId;
                const coreId = treeBlock.dataset.coreId;
                const buildingIndex = treeBlock.dataset.buildingIndex;
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
                } else if (sectionHeader.includes('Crafters') && factoryId) {
                    openEditCrafterModal(id, factoryId, itemId);
                } else if (sectionHeader.includes('Storage') && factoryId) {
                    openEditStorageModal(id, factoryId, itemId);
                } else if (sectionHeader.includes('Non-Production Buildings') && coreId && buildingIndex !== undefined) {
                    openEditNonProdBuildingModal(id, coreId, parseInt(buildingIndex));
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

function renderCraftersTree(crafters, factoryId) {
    const crafterIds = Object.keys(crafters).sort();
    let html = `
        <div class="tree-section" style="margin-left: 20px; margin-top: 10px;">
            <div class="tree-section-header">Crafters (${crafterIds.length})</div>
    `;
    
    if (crafterIds.length === 0) {
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Crafter
            </div>
        `;
    } else {
        crafterIds.forEach(crafterId => {
            const crafter = crafters[crafterId];
            html += `
                <div class="tree-block" data-item-id="${crafterId}" data-factory-id="${factoryId}">
                    <div class="tree-block-label">${crafterId}</div>
                    ${renderItemDetails('Crafters', crafter)}
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Crafter
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function renderStorageTree(storage, factoryId) {
    const storageIds = Object.keys(storage).sort();
    let html = `
        <div class="tree-section" style="margin-left: 20px; margin-top: 10px;">
            <div class="tree-section-header">Storage (${storageIds.length})</div>
    `;
    
    if (storageIds.length === 0) {
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Storage
            </div>
        `;
    } else {
        storageIds.forEach(storageId => {
            const stor = storage[storageId];
            html += `
                <div class="tree-block" data-item-id="${storageId}" data-factory-id="${factoryId}">
                    <div class="tree-block-label">${storageId}</div>
                    ${renderItemDetails('Storage', stor)}
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button" data-factory-id="${factoryId}">
                + Add Storage
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

function renderNonProdBuildingsTree(buildings, coreId) {
    const buildingsArray = Array.isArray(buildings) ? buildings : [];
    let html = `
        <div class="tree-section" style="margin-left: 20px; margin-top: 10px;">
            <div class="tree-section-header">Non-Production Buildings (${buildingsArray.length})</div>
    `;
    
    if (buildingsArray.length === 0) {
        html += `
            <div class="tree-block add-button" data-core-id="${coreId}">
                + Add Non-Production Building
            </div>
        `;
    } else {
        buildingsArray.forEach((building, index) => {
            html += `
                <div class="tree-block" data-building-index="${index}" data-core-id="${coreId}">
                    <div class="tree-block-label">${building.building_id || 'Unknown'}</div>
                    <div class="tree-block-value">Count: ${building.count || 0}</div>
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button" data-core-id="${coreId}">
                + Add Non-Production Building
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
            ${item.building ? `<div class="tree-block-value">Building: ${item.building}</div>` : ''}
            ${item.core_id ? `<div class="tree-block-value">Core: ${item.core_id}</div>` : ''}
        `;
    } else if (sectionType === 'Cores') {
        let html = `
            <div class="tree-block-value">Level: ${item.core_level || 0}</div>
        `;
        // Add non-production buildings as children of core
        if (item.non_production_buildings && item.non_production_buildings.length > 0) {
            html += renderNonProdBuildingsTree(item.non_production_buildings, itemId);
        } else {
            html += renderNonProdBuildingsTree([], itemId);
        }
        return html;
    } else if (sectionType === 'Factories') {
        let html = `
            <div class="tree-block-value">${item.purpose || 'No purpose set'}</div>
        `;
        // Add crafters, storage, receivers, and dispatchers as children of factory
        if (item.machines && item.machines.crafters && Object.keys(item.machines.crafters).length > 0) {
            html += renderCraftersTree(item.machines.crafters, itemId);
        } else {
            html += renderCraftersTree({}, itemId);
        }
        if (item.machines && item.machines.storage && Object.keys(item.machines.storage).length > 0) {
            html += renderStorageTree(item.machines.storage, itemId);
        } else {
            html += renderStorageTree({}, itemId);
        }
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
            ${item.core_id ? `<div class="tree-block-value">Core: ${item.core_id}</div>` : ''}
        `;
    } else if (sectionType === 'Dispatchers') {
        const fromIds = Array.isArray(item.from_ids) ? item.from_ids.join(', ') : item.from_ids || 'None';
        return `
            <div class="tree-block-value">${item.dipatched_item || item.dispatched_item || 'Unknown item'}</div>
            <div class="tree-block-value">Out: ${item.output_rate_limit_ipm || 0} ipm, In: ${item.input_rate_limit_ipm || 0} ipm</div>
            <div class="tree-block-value">From: ${fromIds}</div>
            ${item.building_id ? `<div class="tree-block-value">Building: ${item.building_id}</div>` : ''}
            ${item.core_id ? `<div class="tree-block-value">Core: ${item.core_id}</div>` : ''}
        `;
    } else if (sectionType === 'Crafters') {
        const inputItems = Array.isArray(item.inputs)
            ? item.inputs.map(input => input.input_item).filter(Boolean)
            : [];
        const inputsLabel = inputItems.length > 0 ? inputItems.join(', ') : 'None';
        return `
            <div class="tree-block-value">Crafts: ${item.crafted_item || 'Unknown item'}</div>
            <div class="tree-block-value">Inputs: ${inputsLabel}</div>
            ${item.core_id ? `<div class="tree-block-value">Core: ${item.core_id}</div>` : ''}
        `;
    } else if (sectionType === 'Storage') {
        const storedItem = item.stored_item || 'None';
        return `
            <div class="tree-block-value">Building: ${item.building_id || 'Unknown'}</div>
            <div class="tree-block-value">Item: ${storedItem}</div>
            ${item.num_stacks ? `<div class="tree-block-value">Stacks: ${item.num_stacks}</div>` : ''}
            ${item.core_id ? `<div class="tree-block-value">Core: ${item.core_id}</div>` : ''}
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

function openAddPinModal(gridX, gridY) {
    addPinName.value = 'New Location';
    addPinX.value = gridX;
    addPinY.value = gridY;
    
    addPinModal.classList.add('show');
}

function closeAddPinModal() {
    addPinModal.classList.remove('show');
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

    resourceNodeCoreId.innerHTML = '';
    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '';
    resourceNodeCoreId.appendChild(emptyOption);

    coreIds.forEach(coreId => {
        const option = document.createElement('option');
        option.value = coreId;
        option.textContent = coreId;
        resourceNodeCoreId.appendChild(option);
    });

    if (selectedCoreId && coreIds.includes(selectedCoreId)) {
        resourceNodeCoreId.value = selectedCoreId;
    } else {
        resourceNodeCoreId.value = '';
    }
}

function populateResourceSelectionTable() {
    const tbody = resourceSelectionTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    // rawItemDefinitions should be available from the template
    if (!window.rawItemDefinitions) return;
    
    window.rawItemDefinitions.forEach(item => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';
        row.style.borderBottom = '1px solid #555';
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#404040';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });
        row.addEventListener('click', () => {
            selectResourceRow(item);
        });
        
        row.innerHTML = `
            <td style="border: 1px solid #555; padding: 10px;">${item.item_name}</td>
            <td style="border: 1px solid #555; padding: 10px;">${item.variant}</td>
            <td style="border: 1px solid #555; padding: 10px; text-align: right;">${item.items_per_minute}</td>
            <td style="border: 1px solid #555; padding: 10px;">${item.factory}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function selectResourceRow(item) {
    selectedResourceData = {
        item_name: item.item_name,
        variant: item.variant,
        items_per_minute: item.items_per_minute,
        factory: item.factory
    };
    
    // Update form labels
    resourceItemLabel.textContent = item.item_name;
    resourceVariantLabel.textContent = item.variant;
    resourceRateLabel.textContent = item.items_per_minute + ' ipm';
    resourceBuildingLabel.textContent = item.factory;
    
    closeSelectResourceModal();
}

function openSelectResourceModal() {
    populateResourceSelectionTable();
    selectResourceModal.classList.add('show');
}

function closeSelectResourceModal() {
    selectResourceModal.classList.remove('show');
}

function openAddResourceNodeModal(pinId) {
    selectedPinId = pinId;
    editingResourceNodeId = null;
    selectedResourceData = null;
    resourceNodeModalTitle.textContent = 'Add Resource Node';
    resourceNodeId.value = '';
    resourceNodeId.disabled = false;
    resourceItemLabel.textContent = '-';
    resourceVariantLabel.textContent = '-';
    resourceRateLabel.textContent = '-';
    resourceBuildingLabel.textContent = '-';
    populateResourceNodeCoreOptions(pinId);
    deleteResourceNodeBtn.style.display = 'none';
    resourceNodeModal.classList.add('show');
}

function openEditResourceNodeModal(pinId, nodeId) {
    selectedPinId = pinId;
    editingResourceNodeId = nodeId;
    const node = pins[pinId].resource_nodes[nodeId];
    
    // Restore selected resource data
    selectedResourceData = {
        item_name: node.resource_item,
        variant: node.variant,
        items_per_minute: node.rate_ipm,
        factory: node.building || ''
    };
    
    resourceNodeModalTitle.textContent = 'Edit Resource Node';
    resourceNodeId.value = nodeId;
    resourceNodeId.disabled = true;
    resourceItemLabel.textContent = node.resource_item || '-';
    resourceVariantLabel.textContent = node.variant || '-';
    resourceRateLabel.textContent = (node.rate_ipm || '-') + (node.rate_ipm ? ' ipm' : '');
    resourceBuildingLabel.textContent = node.building || '-';
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
    
    if (!selectedResourceData) {
        alert('Please select a resource using the Select Resource button');
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
    const selectedCoreId = resourceNodeCoreId.value.trim();
    if (selectedCoreId && !coreIds.includes(selectedCoreId)) {
        alert('Please select a valid core ID');
        return;
    }
    
    const nodeData = {
        resource_item: selectedResourceData.item_name,
        rate_ipm: selectedResourceData.items_per_minute,
        variant: selectedResourceData.variant,
        building: selectedResourceData.factory,
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

    const existingFactory = editingFactoryId ? pins[selectedPinId].factories[editingFactoryId] : null;
    const factoryData = {
        purpose: factoryPurpose.value.trim(),
        default_core: selectedCoreId,
        machines: existingFactory && existingFactory.machines ? existingFactory.machines : {}
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

function populateCrafterCoreOptions(pinId, selectedCoreId = '') {
    const cores = (pins[pinId] && pins[pinId].cores) ? pins[pinId].cores : {};
    const coreIds = Object.keys(cores).sort();

    crafterCoreId.innerHTML = '';

    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '';
    crafterCoreId.appendChild(emptyOption);

    coreIds.forEach(coreIdValue => {
        const option = document.createElement('option');
        option.value = coreIdValue;
        option.textContent = coreIdValue;
        crafterCoreId.appendChild(option);
    });

    if (selectedCoreId && coreIds.includes(selectedCoreId)) {
        crafterCoreId.value = selectedCoreId;
    } else {
        crafterCoreId.value = '';
    }
}

function createCrafterInputRow(inputItem, inputData = {}) {
    const row = document.createElement('div');
    row.className = 'crafter-input-row';

    const itemField = document.createElement('div');
    itemField.className = 'crafter-input-field';
    const itemLabel = document.createElement('label');
    itemLabel.textContent = 'Input Item';
    const itemValue = document.createElement('div');
    itemValue.className = 'crafter-input-item';
    itemValue.textContent = inputItem;
    itemValue.style.padding = '8px 12px';
    itemValue.style.backgroundColor = '#2a2a2a';
    itemValue.style.borderRadius = '4px';
    itemValue.style.border = '1px solid #444';
    // Store the value as a data attribute for easy retrieval
    itemValue.dataset.value = inputItem;
    itemField.appendChild(itemLabel);
    itemField.appendChild(itemValue);

    const fromIdsField = document.createElement('div');
    fromIdsField.className = 'crafter-input-field';
    const fromIdsLabel = document.createElement('label');
    fromIdsLabel.textContent = 'From IDs';
    const fromIdsInput = document.createElement('input');
    fromIdsInput.type = 'text';
    fromIdsInput.className = 'crafter-input-from-ids';
    fromIdsInput.placeholder = 'from ids (comma-separated)';
    fromIdsInput.value = Array.isArray(inputData.from_ids)
        ? inputData.from_ids.join(', ')
        : (inputData.from_ids || '');
    fromIdsField.appendChild(fromIdsLabel);
    fromIdsField.appendChild(fromIdsInput);

    const rateField = document.createElement('div');
    rateField.className = 'crafter-input-field';
    const rateLabel = document.createElement('label');
    rateLabel.textContent = 'Rate Limit IPM';
    const rateInput = document.createElement('input');
    rateInput.type = 'number';
    rateInput.className = 'crafter-input-rate';
    rateInput.min = '1';
    rateInput.value = inputData.rate_limit_ipm || 1;
    rateField.appendChild(rateLabel);
    rateField.appendChild(rateInput);

    row.appendChild(itemField);
    row.appendChild(fromIdsField);
    row.appendChild(rateField);

    return row;
}

function resetCrafterInputs() {
    crafterInputsContainer.innerHTML = '';
}

function handleCrafterItemChange() {
    const selectedItem = crafterItem.value;
    resetCrafterInputs();
    
    if (!selectedItem || !window.itemRecipes || !window.itemRecipes[selectedItem]) {
        return; // Show placeholder when no item selected or no recipe found
    }
    
    const recipe = window.itemRecipes[selectedItem];
    // recipe is an array of [inputItemName, quantity] tuples
    // We only care about the input item name (first element)
    recipe.forEach(([inputItemName, _quantity]) => {
        const row = createCrafterInputRow(inputItemName, {});
        crafterInputsContainer.appendChild(row);
    });
}

function populateInputsFromRecipeAndData(selectedItem, existingInputs = []) {
    resetCrafterInputs();
    
    if (!selectedItem || !window.itemRecipes || !window.itemRecipes[selectedItem]) {
        return;
    }
    
    const recipe = window.itemRecipes[selectedItem];
    
    // Create a map of existing input data by input_item for easy lookup
    const existingDataMap = {};
    if (Array.isArray(existingInputs)) {
        existingInputs.forEach(input => {
            existingDataMap[input.input_item] = input;
        });
    }
    
    // Create rows based on recipe, using existing data if available
    recipe.forEach(([inputItemName, _quantity]) => {
        const existingData = existingDataMap[inputItemName] || {};
        const row = createCrafterInputRow(inputItemName, existingData);
        crafterInputsContainer.appendChild(row);
    });
}

// Crafter Modal Functions
function openAddCrafterModal(pinId, factoryId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingCrafterId = null;
    crafterModalTitle.textContent = 'Add Crafter';
    crafterId.value = '';
    crafterId.disabled = false;
    crafterItem.value = '';
    resetCrafterInputs(); // Show placeholder
    populateCrafterCoreOptions(pinId);
    deleteCrafterBtn.style.display = 'none';
    crafterModal.classList.add('show');
}

function openEditCrafterModal(pinId, factoryId, machineId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingCrafterId = machineId;
    const crafter = pins[pinId].factories[factoryId].machines.crafters[machineId];

    crafterModalTitle.textContent = 'Edit Crafter';
    crafterId.value = machineId;
    crafterId.disabled = true;
    crafterItem.value = crafter.crafted_item || '';
    
    // Populate inputs from recipe with existing data
    populateInputsFromRecipeAndData(crafter.crafted_item, crafter.inputs);
    
    populateCrafterCoreOptions(pinId, crafter.core_id || '');
    deleteCrafterBtn.style.display = 'block';
    crafterModal.classList.add('show');
}

function closeCrafterModal() {
    crafterModal.classList.remove('show');
    editingCrafterId = null;
    selectedFactoryId = null;
}

function parseCrafterInputs() {
    const rows = Array.from(crafterInputsContainer.querySelectorAll('.crafter-input-row'));
    const inputs = [];

    for (const row of rows) {
        const inputItemElement = row.querySelector('.crafter-input-item');
        const inputItem = inputItemElement.dataset.value || inputItemElement.textContent.trim();
        const fromIdsValue = row.querySelector('.crafter-input-from-ids').value.trim();
        const rateValue = row.querySelector('.crafter-input-rate').value.trim();

        if (!inputItem) {
            return { error: 'Each input row must include an input item' };
        }

        const rate = parseInt(rateValue);
        if (isNaN(rate) || rate < 1) {
            return { error: 'Each input row must include a positive rate_limit_ipm' };
        }

        const fromIds = fromIdsValue
            ? fromIdsValue.split(',').map(id => id.trim()).filter(id => id)
            : [];

        inputs.push({
            input_item: inputItem,
            from_ids: fromIds,
            rate_limit_ipm: rate
        });
    }

    if (inputs.length === 0) {
        return { error: 'Please add at least one input row' };
    }

    return { inputs };
}

async function handleSaveCrafter() {
    if (!selectedPinId || !selectedFactoryId) return;

    const machineId = crafterId.value.trim();
    if (!machineId) {
        alert('Please enter a crafter ID');
        return;
    }

    const craftedItem = crafterItem.value.trim();
    if (!craftedItem) {
        alert('Please select a crafted item');
        return;
    }

    if (!pins[selectedPinId].factories[selectedFactoryId].machines) {
        pins[selectedPinId].factories[selectedFactoryId].machines = {};
    }
    if (!pins[selectedPinId].factories[selectedFactoryId].machines.crafters) {
        pins[selectedPinId].factories[selectedFactoryId].machines.crafters = {};
    }

    if (!editingCrafterId && pins[selectedPinId].factories[selectedFactoryId].machines.crafters[machineId]) {
        alert('A crafter with this ID already exists');
        return;
    }

    const parseResult = parseCrafterInputs();
    if (parseResult.error) {
        alert(parseResult.error);
        return;
    }

    const crafterData = {
        crafted_item: craftedItem,
        inputs: parseResult.inputs
    };

    const coreIdValue = crafterCoreId.value.trim();
    if (coreIdValue) {
        crafterData.core_id = coreIdValue;
    }

    if (editingCrafterId && editingCrafterId !== machineId) {
        delete pins[selectedPinId].factories[selectedFactoryId].machines.crafters[editingCrafterId];
    }

    pins[selectedPinId].factories[selectedFactoryId].machines.crafters[machineId] = crafterData;

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
            closeCrafterModal();
        }
    } catch (error) {
        console.error('Error saving crafter:', error);
        alert('Error saving crafter');
    }
}

async function handleDeleteCrafter() {
    if (!selectedPinId || !selectedFactoryId || !editingCrafterId) return;

    delete pins[selectedPinId].factories[selectedFactoryId].machines.crafters[editingCrafterId];

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
            closeCrafterModal();
        }
    } catch (error) {
        console.error('Error deleting crafter:', error);
        alert('Error deleting crafter');
    }
}

// Storage Modal Functions
function createStorageInputRow(inputData = {}) {
    const row = document.createElement('div');
    row.className = 'storage-input-row';

    const fromIdsField = document.createElement('div');
    fromIdsField.className = 'storage-input-field';
    const fromIdsLabel = document.createElement('label');
    fromIdsLabel.textContent = 'From IDs';
    const fromIdsInput = document.createElement('input');
    fromIdsInput.type = 'text';
    fromIdsInput.className = 'storage-input-from-ids';
    fromIdsInput.placeholder = 'from ids (comma-separated)';
    fromIdsInput.value = Array.isArray(inputData.from_ids)
        ? inputData.from_ids.join(', ')
        : (inputData.from_ids || '');
    fromIdsField.appendChild(fromIdsLabel);
    fromIdsField.appendChild(fromIdsInput);

    const rateField = document.createElement('div');
    rateField.className = 'storage-input-field';
    const rateLabel = document.createElement('label');
    rateLabel.textContent = 'Rate Limit IPM';
    const rateInput = document.createElement('input');
    rateInput.type = 'number';
    rateInput.className = 'storage-input-rate';
    rateInput.min = '1';
    rateInput.value = inputData.rate_limit_ipm || 1;
    rateField.appendChild(rateLabel);
    rateField.appendChild(rateInput);

    const actions = document.createElement('div');
    actions.className = 'storage-input-actions';
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-danger';
    removeBtn.textContent = 'Remove';
    removeBtn.addEventListener('click', () => {
        row.remove();
    });
    actions.appendChild(removeBtn);

    row.appendChild(fromIdsField);
    row.appendChild(rateField);
    row.appendChild(actions);

    return row;
}

function addStorageInputRow(inputData = {}) {
    storageInputsContainer.appendChild(createStorageInputRow(inputData));
}

function resetStorageInputs() {
    storageInputsContainer.innerHTML = '';
}

function populateStorageCoreOptions(pinId, selectedCoreId = '') {
    const cores = (pins[pinId] && pins[pinId].cores) ? pins[pinId].cores : {};
    const coreIds = Object.keys(cores).sort();

    storageCoreId.innerHTML = '';

    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '';
    storageCoreId.appendChild(emptyOption);

    coreIds.forEach(coreIdValue => {
        const option = document.createElement('option');
        option.value = coreIdValue;
        option.textContent = coreIdValue;
        storageCoreId.appendChild(option);
    });

    if (selectedCoreId && coreIds.includes(selectedCoreId)) {
        storageCoreId.value = selectedCoreId;
    } else {
        storageCoreId.value = '';
    }
}

function openAddStorageModal(pinId, factoryId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingStorageId = null;
    storageModalTitle.textContent = 'Add Storage';
    storageId.value = '';
    storageId.disabled = false;
    storageBuildingId.value = '';
    storageNumStacks.value = '';
    storageStoredItem.value = '*';
    resetStorageInputs();
    addStorageInputRow();
    populateStorageCoreOptions(pinId);
    deleteStorageBtn.style.display = 'none';
    storageModal.classList.add('show');
}

function openEditStorageModal(pinId, factoryId, machineId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingStorageId = machineId;
    const storage = pins[pinId].factories[factoryId].machines.storage[machineId];

    storageModalTitle.textContent = 'Edit Storage';
    storageId.value = machineId;
    storageId.disabled = true;
    storageBuildingId.value = storage.building_id || '';
    storageNumStacks.value = storage.num_stacks || '';
    
    // Set stored item (single value, defaulting to '*' if not set)
    storageStoredItem.value = storage.stored_item || '*';
    
    resetStorageInputs();
    if (Array.isArray(storage.inputs) && storage.inputs.length > 0) {
        storage.inputs.forEach(input => addStorageInputRow(input));
    } else {
        addStorageInputRow();
    }
    
    populateStorageCoreOptions(pinId, storage.core_id || '');
    deleteStorageBtn.style.display = 'block';
    storageModal.classList.add('show');
}

function closeStorageModal() {
    storageModal.classList.remove('show');
    editingStorageId = null;
    selectedFactoryId = null;
}

function parseStorageInputs() {
    const rows = Array.from(storageInputsContainer.querySelectorAll('.storage-input-row'));
    const inputs = [];

    for (const row of rows) {
        const fromIdsValue = row.querySelector('.storage-input-from-ids').value.trim();
        const rateValue = row.querySelector('.storage-input-rate').value.trim();

        const rate = parseInt(rateValue);
        if (isNaN(rate) || rate < 1) {
            return { error: 'Each input row must include a positive rate_limit_ipm' };
        }

        const fromIds = fromIdsValue
            ? fromIdsValue.split(',').map(id => id.trim()).filter(id => id)
            : [];

        inputs.push({
            from_ids: fromIds,
            rate_limit_ipm: rate
        });
    }

    if (inputs.length === 0) {
        return { error: 'Please add at least one input row' };
    }

    return { inputs };
}

async function handleSaveStorage() {
    if (!selectedPinId || !selectedFactoryId) return;

    const machineId = storageId.value.trim();
    if (!machineId) {
        alert('Please enter a storage ID');
        return;
    }

    const buildingId = storageBuildingId.value.trim();
    if (!buildingId) {
        alert('Please select a building');
        return;
    }

    const storedItem = storageStoredItem.value.trim();
    if (!storedItem) {
        alert('Please select a stored item');
        return;
    }

    if (!pins[selectedPinId].factories[selectedFactoryId].machines) {
        pins[selectedPinId].factories[selectedFactoryId].machines = {};
    }
    if (!pins[selectedPinId].factories[selectedFactoryId].machines.storage) {
        pins[selectedPinId].factories[selectedFactoryId].machines.storage = {};
    }

    if (!editingStorageId && pins[selectedPinId].factories[selectedFactoryId].machines.storage[machineId]) {
        alert('A storage with this ID already exists');
        return;
    }

    const parseResult = parseStorageInputs();
    if (parseResult.error) {
        alert(parseResult.error);
        return;
    }

    const storageData = {
        building_id: buildingId,
        stored_item: storedItem,
        inputs: parseResult.inputs
    };

    const numStacks = storageNumStacks.value.trim();
    if (numStacks) {
        const stacksInt = parseInt(numStacks);
        if (!isNaN(stacksInt) && stacksInt > 0) {
            storageData.num_stacks = stacksInt;
        }
    }

    const coreIdValue = storageCoreId.value.trim();
    if (coreIdValue) {
        storageData.core_id = coreIdValue;
    }

    if (editingStorageId && editingStorageId !== machineId) {
        delete pins[selectedPinId].factories[selectedFactoryId].machines.storage[editingStorageId];
    }

    pins[selectedPinId].factories[selectedFactoryId].machines.storage[machineId] = storageData;

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
            closeStorageModal();
        }
    } catch (error) {
        console.error('Error saving storage:', error);
        alert('Error saving storage');
    }
}

async function handleDeleteStorage() {
    if (!selectedPinId || !selectedFactoryId || !editingStorageId) return;

    delete pins[selectedPinId].factories[selectedFactoryId].machines.storage[editingStorageId];

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
            closeStorageModal();
        }
    } catch (error) {
        console.error('Error deleting storage:', error);
        alert('Error deleting storage');
    }
}

// Receiver Modal Functions
function populateReceiverCoreOptions(pinId, selectedCoreId = '') {
    const cores = (pins[pinId] && pins[pinId].cores) ? pins[pinId].cores : {};
    const coreIds = Object.keys(cores).sort();

    receiverCoreId.innerHTML = '';

    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '';
    receiverCoreId.appendChild(emptyOption);

    coreIds.forEach(coreIdValue => {
        const option = document.createElement('option');
        option.value = coreIdValue;
        option.textContent = coreIdValue;
        receiverCoreId.appendChild(option);
    });

    if (selectedCoreId && coreIds.includes(selectedCoreId)) {
        receiverCoreId.value = selectedCoreId;
    } else {
        receiverCoreId.value = '';
    }
}

function handleReceiverBuildingChange() {
    const buildingId = receiverBuildingId.value.trim();
    
    if (buildingId) {
        // Show core field and populate options
        receiverCoreGroup.style.display = 'block';
        if (selectedPinId) {
            populateReceiverCoreOptions(selectedPinId);
        }
    } else {
        // Hide core field and clear value
        receiverCoreGroup.style.display = 'none';
        receiverCoreId.value = '';
    }
}

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
    receiverCoreGroup.style.display = 'none';
    receiverCoreId.value = '';
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
    
    // Show/hide core field based on building selection
    if (receiver.building_id) {
        receiverCoreGroup.style.display = 'block';
        populateReceiverCoreOptions(pinId, receiver.core_id || '');
    } else {
        receiverCoreGroup.style.display = 'none';
        receiverCoreId.value = '';
    }
    
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
    
    // Add core_id if building is selected and core is specified
    const buildingIdValue = receiverBuildingId.value.trim();
    if (buildingIdValue) {
        const coreIdValue = receiverCoreId.value.trim();
        if (coreIdValue) {
            receiverData.core_id = coreIdValue;
        }
    }
    
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
function populateDispatcherCoreOptions(pinId, selectedCoreId = '') {
    const pin = pins[pinId];
    dispatcherCoreId.innerHTML = '<option value=""></option>';
    
    if (pin && pin.cores) {
        for (const coreId in pin.cores) {
            const option = document.createElement('option');
            option.value = coreId;
            option.textContent = coreId;
            if (coreId === selectedCoreId) {
                option.selected = true;
            }
            dispatcherCoreId.appendChild(option);
        }
    }
}

function handleDispatcherBuildingChange() {
    if (dispatcherBuildingId.value) {
        dispatcherCoreGroup.style.display = 'block';
        if (selectedPinId) {
            populateDispatcherCoreOptions(selectedPinId, dispatcherCoreId.value);
        }
    } else {
        dispatcherCoreGroup.style.display = 'none';
        dispatcherCoreId.value = '';
    }
}

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
    dispatcherCoreGroup.style.display = 'none';
    dispatcherCoreId.value = '';
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
    
    // Show/hide core field based on building selection
    if (dispatcher.building_id) {
        dispatcherCoreGroup.style.display = 'block';
        populateDispatcherCoreOptions(pinId, dispatcher.core_id || '');
    } else {
        dispatcherCoreGroup.style.display = 'none';
        dispatcherCoreId.value = '';
    }
    
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
    
    // Add core_id only if building is selected and core is specified
    if (dispatcherBuildingId.value.trim() && dispatcherCoreId.value.trim()) {
        dispatcherData.core_id = dispatcherCoreId.value.trim();
    }
    
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

// Non-Production Building Modal Functions
function openAddNonProdBuildingModal(pinId, coreId) {
    selectedPinId = pinId;
    selectedCoreId = coreId;
    editingBuildingIndex = null;
    nonProdBuildingModalTitle.textContent = 'Add Non-Production Building';
    nonProdBuildingId.value = '';
    nonProdBuildingId.disabled = false;
    nonProdBuildingCount.value = 1;
    deleteNonProdBuildingBtn.style.display = 'none';
    nonProdBuildingModal.classList.add('show');
}

function openEditNonProdBuildingModal(pinId, coreId, buildingIndex) {
    selectedPinId = pinId;
    selectedCoreId = coreId;
    editingBuildingIndex = buildingIndex;
    const building = pins[pinId].cores[coreId].non_production_buildings[buildingIndex];
    
    nonProdBuildingModalTitle.textContent = 'Edit Non-Production Building';
    nonProdBuildingId.value = building.building_id || '';
    nonProdBuildingId.disabled = false;
    nonProdBuildingCount.value = building.count || 1;
    deleteNonProdBuildingBtn.style.display = 'block';
    nonProdBuildingModal.classList.add('show');
}

function closeNonProdBuildingModal() {
    nonProdBuildingModal.classList.remove('show');
    editingBuildingIndex = null;
    selectedCoreId = null;
}

async function handleSaveNonProdBuilding() {
    if (!selectedPinId || !selectedCoreId) return;
    
    const buildingId = nonProdBuildingId.value.trim();
    if (!buildingId) {
        alert('Please select a building');
        return;
    }
    
    const count = parseInt(nonProdBuildingCount.value);
    if (isNaN(count) || count < 1) {
        alert('Please enter a valid count (minimum 1)');
        return;
    }
    
    // Initialize non_production_buildings if needed
    if (!pins[selectedPinId].cores[selectedCoreId].non_production_buildings) {
        pins[selectedPinId].cores[selectedCoreId].non_production_buildings = [];
    }
    
    const buildingData = {
        building_id: buildingId,
        count: count
    };
    
    if (editingBuildingIndex !== null) {
        // Editing existing building
        pins[selectedPinId].cores[selectedCoreId].non_production_buildings[editingBuildingIndex] = buildingData;
    } else {
        // Adding new building
        pins[selectedPinId].cores[selectedCoreId].non_production_buildings.push(buildingData);
    }
    
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
            closeNonProdBuildingModal();
        }
    } catch (error) {
        console.error('Error saving non-production building:', error);
        alert('Error saving non-production building');
    }
}

async function handleDeleteNonProdBuilding() {
    if (!selectedPinId || !selectedCoreId || editingBuildingIndex === null) return;
    
    pins[selectedPinId].cores[selectedCoreId].non_production_buildings.splice(editingBuildingIndex, 1);
    
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
            closeNonProdBuildingModal();
        }
    } catch (error) {
        console.error('Error deleting non-production building:', error);
        alert('Error deleting non-production building');
    }
}
