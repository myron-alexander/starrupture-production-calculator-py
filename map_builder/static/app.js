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
const receiverSelectDispatcherBtn = document.getElementById('receiverSelectDispatcherBtn');
const receiverSiteLabel = document.getElementById('receiverSiteLabel');
const receiverFactoryLabel = document.getElementById('receiverFactoryLabel');
const receiverDispatcherLabel = document.getElementById('receiverDispatcherLabel');
const receiverBuildingId = document.getElementById('receiverBuildingId');
const receiverCoreGroup = document.getElementById('receiverCoreGroup');
const receiverCoreId = document.getElementById('receiverCoreId');
const saveReceiverBtn = document.getElementById('saveReceiverBtn');
const deleteReceiverBtn = document.getElementById('deleteReceiverBtn');

// Receiver Dispatcher Selector Modal Elements
const selectReceiverDispatcherModal = document.getElementById('selectReceiverDispatcherModal');
const receiverDispatcherSelectionTable = document.getElementById('receiverDispatcherSelectionTable');

let selectedReceiverDispatcher = null;

// Dispatcher Modal Elements
const dispatcherModal = document.getElementById('dispatcherModal');
const dispatcherModalTitle = document.getElementById('dispatcherModalTitle');
const dispatcherId = document.getElementById('dispatcherId');
const dispatchedItem = document.getElementById('dispatchedItem');
const dispatcherOutputRate = document.getElementById('dispatcherOutputRate');
const dispatcherInputRate = document.getElementById('dispatcherInputRate');
const dispatcherFromIdsBadges = document.getElementById('dispatcherFromIdsBadges');
const dispatcherSelectSourcesBtn = document.getElementById('dispatcherSelectSourcesBtn');
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
const duplicateCrafterBtn = document.getElementById('duplicateCrafterBtn');
const deleteCrafterBtn = document.getElementById('deleteCrafterBtn');

// Crafter Source Selector Modal Elements
const selectCrafterSourcesModal = document.getElementById('selectCrafterSourcesModal');
const crafterSourcesSelectionTable = document.getElementById('crafterSourcesSelectionTable');
const selectAllSourcesCheckbox = document.getElementById('selectAllSourcesCheckbox');
const selectSourcesBtn = document.getElementById('selectSourcesBtn');

// Dispatcher Source Selector Modal Elements
const selectDispatcherSourcesModal = document.getElementById('selectDispatcherSourcesModal');
const dispatcherSourcesSelectionTable = document.getElementById('dispatcherSourcesSelectionTable');
const selectAllDispatcherSourcesCheckbox = document.getElementById('selectAllDispatcherSourcesCheckbox');
const selectDispatcherSourcesBtn = document.getElementById('selectDispatcherSourcesBtn');

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
const duplicateStorageBtn = document.getElementById('duplicateStorageBtn');
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
    // Check if image is already loaded (from cache)
    if (mapImage.complete && mapImage.naturalHeight !== 0) {
        loadPins();
        attachEventListeners();
    } else {
        mapImage.onload = () => {
            loadPins();
            attachEventListeners();
        };
    }
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
    document.getElementById('addPinForm').addEventListener('submit', (e) => {
        e.preventDefault();
        handleAddPin();
    });

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
    document.getElementById('resourceNodeForm').addEventListener('submit', (e) => {
        e.preventDefault();
        handleSaveResourceNode();
    });
    deleteResourceNodeBtn.addEventListener('click', handleDeleteResourceNode);

    // Core Modal controls
    document.querySelectorAll('[data-modal="coreModal"]').forEach(el => {
        el.addEventListener('click', closeCoreModal);
    });
    document.getElementById('coreForm').addEventListener('submit', (e) => {
        e.preventDefault();
        handleSaveCore();
    });
    deleteCoreBtn.addEventListener('click', handleDeleteCore);

    // Factory Modal controls
    document.querySelectorAll('[data-modal="factoryModal"]').forEach(el => {
        el.addEventListener('click', closeFactoryModal);
    });
    document.getElementById('factoryForm').addEventListener('submit', (e) => {
        e.preventDefault();
        handleSaveFactory();
    });
    deleteFactoryBtn.addEventListener('click', handleDeleteFactory);

    // Receiver Modal controls
    document.querySelectorAll('[data-modal="receiverModal"]').forEach(el => {
        el.addEventListener('click', closeReceiverModal);
    });
    receiverBuildingId.addEventListener('change', handleReceiverBuildingChange);
    receiverSelectDispatcherBtn.addEventListener('click', openSelectReceiverDispatcherModal);
    document.getElementById('receiverForm').addEventListener('submit', (e) => {
        e.preventDefault();
        handleSaveReceiver();
    });
    deleteReceiverBtn.addEventListener('click', handleDeleteReceiver);

    // Receiver Dispatcher Selector Modal controls
    document.querySelectorAll('[data-modal="selectReceiverDispatcherModal"]').forEach(el => {
        el.addEventListener('click', closeSelectReceiverDispatcherModal);
    });

    // Dispatcher Modal controls
    document.querySelectorAll('[data-modal="dispatcherModal"]').forEach(el => {
        el.addEventListener('click', closeDispatcherModal);
    });
    dispatcherBuildingId.addEventListener('change', handleDispatcherBuildingChange);
    dispatcherSelectSourcesBtn.addEventListener('click', openSelectDispatcherSourcesModal);
    saveDispatcherBtn.addEventListener('click', handleSaveDispatcher);
    deleteDispatcherBtn.addEventListener('click', handleDeleteDispatcher);

    // Crafter Modal controls
    document.querySelectorAll('[data-modal="crafterModal"]').forEach(el => {
        el.addEventListener('click', closeCrafterModal);
    });
    crafterItem.addEventListener('change', handleCrafterItemChange);
    saveCrafterBtn.addEventListener('click', handleSaveCrafter);
    duplicateCrafterBtn.addEventListener('click', handleDuplicateCrafter);
    deleteCrafterBtn.addEventListener('click', handleDeleteCrafter);

    // Crafter Source Selector Modal controls
    document.querySelectorAll('[data-modal="selectCrafterSourcesModal"]').forEach(el => {
        el.addEventListener('click', closeSelectCrafterSourcesModal);
    });
    selectAllSourcesCheckbox.addEventListener('change', handleSelectAllSources);
    selectSourcesBtn.addEventListener('click', handleSelectSources);

    // Dispatcher Source Selector Modal controls
    document.querySelectorAll('[data-modal="selectDispatcherSourcesModal"]').forEach(el => {
        el.addEventListener('click', closeSelectDispatcherSourcesModal);
    });
    selectAllDispatcherSourcesCheckbox.addEventListener('change', handleSelectAllDispatcherSources);
    selectDispatcherSourcesBtn.addEventListener('click', handleSelectDispatcherSources);

    // Add event delegation for "Select Sources" buttons in crafter input rows
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('crafter-select-sources-btn')) {
            openSelectCrafterSourcesModal(e.target);
        }
        if (e.target.classList.contains('storage-select-sources-btn')) {
            openSelectStorageSourcesModal(e.target);
        }
    });

    // Storage Modal controls
    document.querySelectorAll('[data-modal="storageModal"]').forEach(el => {
        el.addEventListener('click', closeStorageModal);
    });
    document.querySelectorAll('[data-modal="selectStorageSourcesModal"]').forEach(el => {
        el.addEventListener('click', closeSelectStorageSourcesModal);
    });
    storageStoredItem.addEventListener('change', () => {
        // If stored item changes to anything other than asterisk, clear the inputs list
        if (storageStoredItem.value !== '*') {
            resetStorageInputs();
            addStorageInputRow();
        }
    });
    addStorageInputBtn.addEventListener('click', () => {
        addStorageInputRow();
    });
    saveStorageBtn.addEventListener('click', handleSaveStorage);
    duplicateStorageBtn.addEventListener('click', handleDuplicateStorage);
    deleteStorageBtn.addEventListener('click', handleDeleteStorage);

    const selectAllStorageSourcesCheckbox = document.getElementById('selectAllStorageSourcesCheckbox');
    if (selectAllStorageSourcesCheckbox) {
        selectAllStorageSourcesCheckbox.addEventListener('change', handleSelectAllStorageSources);
    }
    const selectStorageSourcesBtn = document.getElementById('selectStorageSourcesBtn');
    if (selectStorageSourcesBtn) {
        selectStorageSourcesBtn.addEventListener('click', handleSelectStorageSources);
    }

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

    // Escape key closes any open modal
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            // Close modals in order of priority (nested modals first)
            if (selectResourceModal.classList.contains('show')) {
                closeSelectResourceModal();
            } else if (selectCrafterSourcesModal.classList.contains('show')) {
                closeSelectCrafterSourcesModal();
            } else if (selectStorageSourcesModal.classList.contains('show')) {
                closeSelectStorageSourcesModal();
            } else if (selectDispatcherSourcesModal.classList.contains('show')) {
                closeSelectDispatcherSourcesModal();
            } else if (selectReceiverDispatcherModal.classList.contains('show')) {
                closeSelectReceiverDispatcherModal();
            } else if (addPinModal.classList.contains('show')) {
                closeAddPinModal();
            } else if (editModal.classList.contains('show')) {
                closeEditModal();
            } else if (resourceNodeModal.classList.contains('show')) {
                closeResourceNodeModal();
            } else if (coreModal.classList.contains('show')) {
                closeCoreModal();
            } else if (factoryModal.classList.contains('show')) {
                closeFactoryModal();
            } else if (receiverModal.classList.contains('show')) {
                closeReceiverModal();
            } else if (dispatcherModal.classList.contains('show')) {
                closeDispatcherModal();
            } else if (crafterModal.classList.contains('show')) {
                closeCrafterModal();
            } else if (storageModal.classList.contains('show')) {
                closeStorageModal();
            } else if (nonProdBuildingModal.classList.contains('show')) {
                closeNonProdBuildingModal();
            }
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

    const hasConflict = Object.entries(pins).some(([id, pin]) => {
        if (id === name) return true;
        if (pin.name && pin.name === name) return true;
        return false;
    });
    if (hasConflict) {
        alert('Site name must be globally unique');
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
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Error adding pin');
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
        Object.entries(pins).forEach(([id, pin]) => {
            if (!pin.id) {
                pin.id = id;
            }
        });
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
        tooltip.innerHTML = `<strong>${pin.id}</strong><br>Grid: (${pin.x}, ${pin.y})`;

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
                <div class="pin-item-name">${index + 1}. ${pin.id}</div>
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

        /*
         * =============
         * = IMPORTANT =
         * =============
         * When changing the value passed into parameter sectionHeader of renderTreeSection
         * (the first parameter), you must change the corresponding value in function
         * renderItemDetails as it uses the value to determine how to render the items.
         */

        // Add Resource Nodes section.
        detailsHTML += renderTreeSection('Resource Nodes', 'Resource Node', pin.resource_nodes || {});

        // Add Cores section
        detailsHTML += renderTreeSection('Cores', 'Core', pin.cores || {});

        // Add Factories section
        detailsHTML += renderTreeSection('Factories', 'Factory', pin.factories || {}, id);

        details.innerHTML = detailsHTML;

        pinItem.appendChild(header);
        pinItem.appendChild(details);

        // Restore expanded state from localStorage
        if (loadPinExpandedState(id)) {
            details.classList.add('expanded');
            const toggle = header.querySelector('.pin-item-toggle');
            toggle.textContent = '▲';
        }

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
            const factoryToggle = e.target.closest('.factory-item-toggle');
            const addBtn = e.target.closest('.add-button');
            const visualizeBtn = e.target.closest('.visualize-factory-btn');
            const treeBlock = e.target.closest('.tree-block:not(.add-button)');

            if (factoryToggle) {
                e.stopPropagation();
                const togglePinId = factoryToggle.dataset.pinId || id;
                const factoryId = factoryToggle.dataset.factoryId;
                if (factoryId) {
                    toggleFactoryDetails(togglePinId, factoryId, factoryToggle);
                }
            } else if (visualizeBtn) {
                const factoryId = visualizeBtn.dataset.factoryId;
                //openFactoryVisualization(id, factoryId);
                openFactoryVisualizationDirectRender(id, factoryId);
            } else if (addBtn) {
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

/*
Note that the title value is used by renderItemDetails to determine what section to render
thus the title value is significant. Unfortunately, my AI junior designed this in a way that
sets the add button for factories to "Add Factorie" which is not valid english and should be
"Add Factory". The simple fix is to split the purpose of title into section header and component
name.
*/
function renderTreeSection(sectionHeader, componentName, items, parentPinId = null) {
    const itemIds = Object.keys(items).sort(); // Sort alphabetically
    let html = `
        <div class="tree-section">
            <div class="tree-section-header">${sectionHeader} (${itemIds.length})</div>
    `;

    if (itemIds.length === 0) {
        html += `
            <div class="tree-block add-button">
                + Add ${componentName}
            </div>
        `;
    } else {
        itemIds.forEach(itemId => {
            const item = items[itemId];
            const isFactory = sectionHeader === 'Factories';
            const factoryAttrs = isFactory
                ? ` data-pin-id="${parentPinId || ''}" data-item-type="factory"`
                : '';
            html += `
                <div class="tree-block" data-item-id="${itemId}"${factoryAttrs}>
                    <div class="tree-block-label">${itemId}</div>
                    ${renderItemDetails(sectionHeader, item, itemId, parentPinId)}
                </div>
            `;
        });
        html += `
            <div class="tree-block add-button">
                + Add ${componentName}
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

function renderItemDetails(sectionType, item, itemId = null, parentPinId = null) {
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
        const isCollapsed = parentPinId ? loadFactoryCollapsedState(parentPinId, itemId) : false;
        let html = `
            <div class="tree-block-value">${item.purpose || 'No purpose set'}</div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 8px;">
                <button class="visualize-factory-btn" data-factory-id="${itemId}" style="padding: 4px 8px; font-size: 12px; cursor: pointer;">Visualize</button>
                <span class="pin-item-toggle factory-item-toggle" data-pin-id="${parentPinId || ''}" data-factory-id="${itemId}" title="${isCollapsed ? 'Expand factory' : 'Collapse factory'}">${isCollapsed ? '▼' : '▲'}</span>
            </div>
            <div class="factory-children" style="${isCollapsed ? 'display: none;' : ''}">
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
        html += '</div>';
        return html;
    } else if (sectionType === 'Receivers') {
        // Look up the dispatcher to get the item being received
        let receivedItem = 'Unknown item';
        const dispatcher = pins[item.site_id]?.factories[item.factory_id]?.dispatchers[item.dispatcher_id];
        if (dispatcher) {
            receivedItem = dispatcher.dispatched_item || dispatcher.dipatched_item || 'Unknown item';
        }

        return `
            <div class="tree-block-value">Item: ${receivedItem}</div>
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
        savePinExpandedState(pinId, false);
    } else {
        details.classList.add('expanded');
        toggle.textContent = '▲';
        savePinExpandedState(pinId, true);
    }
}

function savePinExpandedState(pinId, isExpanded) {
    try {
        const expandedPins = JSON.parse(localStorage.getItem('expandedPins') || '{}');
        expandedPins[pinId] = isExpanded;
        localStorage.setItem('expandedPins', JSON.stringify(expandedPins));
    } catch (e) {
        console.error('Error saving pin expanded state:', e);
    }
}

function loadPinExpandedState(pinId) {
    try {
        const expandedPins = JSON.parse(localStorage.getItem('expandedPins') || '{}');
        return expandedPins[pinId] === true;
    } catch (e) {
        console.error('Error loading pin expanded state:', e);
        return false;
    }
}

function saveFactoryCollapsedState(pinId, factoryId, isCollapsed) {
    try {
        const collapsedFactories = JSON.parse(localStorage.getItem('collapsedFactories') || '{}');
        if (!collapsedFactories[pinId]) {
            collapsedFactories[pinId] = {};
        }
        collapsedFactories[pinId][factoryId] = isCollapsed;
        localStorage.setItem('collapsedFactories', JSON.stringify(collapsedFactories));
    } catch (e) {
        console.error('Error saving factory collapsed state:', e);
    }
}

function loadFactoryCollapsedState(pinId, factoryId) {
    try {
        const collapsedFactories = JSON.parse(localStorage.getItem('collapsedFactories') || '{}');
        return collapsedFactories[pinId] && collapsedFactories[pinId][factoryId] === true;
    } catch (e) {
        console.error('Error loading factory collapsed state:', e);
        return false;
    }
}

function toggleFactoryDetails(pinId, factoryId, toggleElement) {
    const treeBlock = toggleElement.closest('.tree-block');
    const children = treeBlock ? treeBlock.querySelector('.factory-children') : null;
    if (!children) return;

    const isCollapsed = children.style.display === 'none';

    if (isCollapsed) {
        children.style.display = '';
        toggleElement.textContent = '▲';
        toggleElement.title = 'Collapse factory';
        saveFactoryCollapsedState(pinId, factoryId, false);
    } else {
        children.style.display = 'none';
        toggleElement.textContent = '▼';
        toggleElement.title = 'Expand factory';
        saveFactoryCollapsedState(pinId, factoryId, true);
    }
}

function openAddPinModal(gridX, gridY) {
    addPinName.value = '';
    addPinX.value = gridX;
    addPinY.value = gridY;

    addPinModal.classList.add('show');
    addPinName.focus()
}

function closeAddPinModal() {
    addPinModal.classList.remove('show');
}

function openEditModal(pinId) {
    selectedPinId = pinId;
    const pin = pins[pinId];

    editPinName.value = pin.id;
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

    const hasConflict = Object.entries(pins).some(([id, pin]) => {
        if (id === selectedPinId) return false;
        if (id === name) return true;
        if (pin.name && pin.name === name) return true;
        return false;
    });
    if (hasConflict) {
        alert('Site name must be globally unique');
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
            const previousId = selectedPinId;
            if (updatedPin.id !== selectedPinId) {
                delete pins[selectedPinId];
                selectedPinId = updatedPin.id;
                // Update localStorage key for expanded state
                try {
                    const expandedPins = JSON.parse(localStorage.getItem('expandedPins') || '{}');
                    if (expandedPins[previousId] !== undefined) {
                        expandedPins[updatedPin.id] = expandedPins[previousId];
                        delete expandedPins[previousId];
                        localStorage.setItem('expandedPins', JSON.stringify(expandedPins));
                    }
                } catch (e) {
                    console.error('Error updating pin expanded state:', e);
                }
            }
            pins[updatedPin.id] = updatedPin;
            renderPins();
            renderPinsList();
            closeEditModal();
            if (updatedPin.id !== previousId) {
                loadPins();
            }
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Error saving site');
        }
    } catch (error) {
        console.error('Error saving pin:', error);
        alert('Error saving pin');
    }
}

async function handleDeletePin() {
    if (!selectedPinId) return;

    try {
        // Before deleting the site, find and remove all receivers that reference dispatchers from this site
        const deletedSiteId = selectedPinId;
        const deletedSite = pins[deletedSiteId];

        // Collect all dispatcher IDs from all factories in the site being deleted
        const deletedDispatchers = [];
        if (deletedSite && deletedSite.factories) {
            for (const [factoryId, factory] of Object.entries(deletedSite.factories)) {
                if (factory.dispatchers) {
                    for (const dispatcherId of Object.keys(factory.dispatchers)) {
                        deletedDispatchers.push({ factoryId, dispatcherId });
                    }
                }
            }
        }

        // Find and delete receivers in other sites that reference these dispatchers
        for (const [siteId, site] of Object.entries(pins)) {
            if (siteId === deletedSiteId) continue; // Skip the site being deleted

            if (site.factories) {
                for (const [factoryId, factory] of Object.entries(site.factories)) {
                    if (factory.receivers) {
                        const receiversToDelete = [];
                        for (const [receiverId, receiver] of Object.entries(factory.receivers)) {
                            // Check if this receiver references a dispatcher from the deleted site
                            if (receiver.site_id === deletedSiteId) {
                                receiversToDelete.push(receiverId);
                            }
                        }

                        // Delete the receivers
                        receiversToDelete.forEach(receiverId => {
                            delete factory.receivers[receiverId];
                        });

                        // If any receivers were deleted, update the site
                        if (receiversToDelete.length > 0) {
                            // Save the updated factory/site
                            fetch(`/api/pins/${siteId}`, {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ factories: site.factories })
                            }).catch(error => {
                                console.error(`Error updating site ${siteId}:`, error);
                            });
                        }
                    }
                }
            }
        }

        // Now delete the site
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            delete pins[selectedPinId];
            // Clean up expanded state from localStorage
            try {
                const expandedPins = JSON.parse(localStorage.getItem('expandedPins') || '{}');
                delete expandedPins[selectedPinId];
                localStorage.setItem('expandedPins', JSON.stringify(expandedPins));
            } catch (e) {
                console.error('Error cleaning up pin expanded state:', e);
            }
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

    // When the selector is closed, move the cursor to the resource id so that the id can be
    // set to a name that makes sense for the selected resource.
    resourceNodeId.focus()
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
    openSelectResourceModal();
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
    resourceNodeId.disabled = false;
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

function getFactoryIdConflicts(factory, candidateId, exclude = null) {
    const conflicts = [];
    const machines = factory && factory.machines ? factory.machines : {};

    const checkMap = (map, type) => {
        if (!map) return;
        if (Object.prototype.hasOwnProperty.call(map, candidateId)) {
            if (!exclude || exclude.type !== type || exclude.id !== candidateId) {
                conflicts.push(type);
            }
        }
    };

    checkMap(machines.crafters, 'crafter');
    checkMap(machines.storage, 'storage');
    checkMap(factory.receivers, 'receiver');
    checkMap(factory.dispatchers, 'dispatcher');

    return conflicts;
}

function getSiteFactoryIdConflicts(pin, candidateId) {
    const results = [];
    const factories = pin && pin.factories ? pin.factories : {};

    for (const [factoryId, factory] of Object.entries(factories)) {
        const conflicts = getFactoryIdConflicts(factory, candidateId);
        if (conflicts.length) {
            results.push({ factoryId, conflicts });
        }
    }

    return results;
}

function removeFromIdsReference(deletedId, pinId = null, factoryId = null) {
    // Helper to normalize and filter from_ids array
    const normalizeAndFilter = (fromIds) => {
        let idsArray = [];
        if (Array.isArray(fromIds)) {
            idsArray = [...fromIds];
        } else if (typeof fromIds === 'string') {
            idsArray = fromIds.split(/,\s*/).map(id => id.trim()).filter(id => id);
        }
        const filtered = idsArray.filter(id => id !== deletedId);
        if (filtered.length !== idsArray.length) {
            console.log(`Removed "${deletedId}" from from_ids: [${idsArray}] -> [${filtered}]`);
        }
        return filtered;
    };

    console.log(`removeFromIdsReference called with deletedId="${deletedId}", pinId="${pinId}", factoryId="${factoryId}"`);

    if (pinId && factoryId) {
        // Clean up only the specific factory
        const factory = pins[pinId]?.factories?.[factoryId];
        console.log(`Cleaning specific factory: ${factoryId} in pin ${pinId}`);
        if (factory) {
            // Remove from crafters
            const crafters = factory.machines?.crafters || {};
            console.log('Crafters found:', Object.keys(crafters));
            for (const [crafterId, crafter] of Object.entries(crafters)) {
                if (crafter.inputs && Array.isArray(crafter.inputs)) {
                    for (const input of crafter.inputs) {
                        if (input.from_ids) {
                            input.from_ids = normalizeAndFilter(input.from_ids);
                        }
                    }
                }
            }

            // Remove from storage
            const storage = factory.machines?.storage || {};
            console.log('Storage found:', Object.keys(storage));
            for (const [storageId, storageItem] of Object.entries(storage)) {
                if (storageItem.inputs && Array.isArray(storageItem.inputs)) {
                    for (const input of storageItem.inputs) {
                        if (input.from_ids) {
                            input.from_ids = normalizeAndFilter(input.from_ids);
                        }
                    }
                }
            }

            // Remove from dispatchers
            const dispatchers = factory.dispatchers || {};
            console.log('Dispatchers found:', Object.keys(dispatchers));
            for (const [dispatcherId, dispatcher] of Object.entries(dispatchers)) {
                if (dispatcher.from_ids) {
                    dispatcher.from_ids = normalizeAndFilter(dispatcher.from_ids);
                }
            }
        }
    } else if (pinId) {
        // Clean up all factories in the pin (for site-level deletions)
        const pin = pins[pinId];
        console.log(`Cleaning all factories in pin ${pinId}`);
        if (pin) {
            const factories = pin.factories || {};
            console.log('All factories in pin:', Object.keys(factories));
            for (const [fId, factory] of Object.entries(factories)) {
                console.log(`  Processing factory: ${fId}`);
                // Remove from crafters
                const crafters = factory.machines?.crafters || {};
                console.log(`    Crafters found: ${Object.keys(crafters)}`);
                for (const [crafterId, crafter] of Object.entries(crafters)) {
                    if (crafter.inputs && Array.isArray(crafter.inputs)) {
                        for (const input of crafter.inputs) {
                            if (input.from_ids) {
                                input.from_ids = normalizeAndFilter(input.from_ids);
                            }
                        }
                    }
                }

                // Remove from storage
                const storage = factory.machines?.storage || {};
                console.log(`    Storage found: ${Object.keys(storage)}`);
                for (const [storageId, storageItem] of Object.entries(storage)) {
                    if (storageItem.inputs && Array.isArray(storageItem.inputs)) {
                        for (const input of storageItem.inputs) {
                            if (input.from_ids) {
                                input.from_ids = normalizeAndFilter(input.from_ids);
                            }
                        }
                    }
                }

                // Remove from dispatchers
                const dispatchers = factory.dispatchers || {};
                console.log(`    Dispatchers found: ${Object.keys(dispatchers)}`);
                for (const [dispatcherId, dispatcher] of Object.entries(dispatchers)) {
                    if (dispatcher.from_ids) {
                        dispatcher.from_ids = normalizeAndFilter(dispatcher.from_ids);
                    }
                }
            }
        }
    }
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

    // Check for duplicate ID (allow current ID when editing)
    if (pins[selectedPinId].resource_nodes && pins[selectedPinId].resource_nodes[nodeId]) {
        if (!editingResourceNodeId || editingResourceNodeId !== nodeId) {
            alert('A resource node with this ID already exists');
            return;
        }
    }

    // Ensure resource ID does not conflict with any factory entity IDs in this site
    const pin = pins[selectedPinId];
    const factoryConflicts = getSiteFactoryIdConflicts(pin, nodeId);
    if (factoryConflicts.length > 0) {
        const firstConflict = factoryConflicts[0];
        alert(`Resource ID conflicts with existing ${firstConflict.conflicts.join(', ')} ID in factory ${firstConflict.factoryId}`);
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

    // If editing and ID changed, delete old entry and update all from_ids references
    if (editingResourceNodeId && editingResourceNodeId !== nodeId) {
        delete pins[selectedPinId].resource_nodes[editingResourceNodeId];

        // Update all from_ids references across all factories in this site
        const factories = pins[selectedPinId].factories || {};
        for (const [factoryId, factory] of Object.entries(factories)) {
            // Update crafters
            const crafters = factory.machines?.crafters || {};
            for (const crafter of Object.values(crafters)) {
                if (crafter.inputs && Array.isArray(crafter.inputs)) {
                    for (const input of crafter.inputs) {
                        if (input.from_ids && Array.isArray(input.from_ids)) {
                            const index = input.from_ids.indexOf(editingResourceNodeId);
                            if (index !== -1) {
                                input.from_ids[index] = nodeId;
                            }
                        }
                    }
                }
            }

            // Update storage
            const storage = factory.machines?.storage || {};
            for (const storageItem of Object.values(storage)) {
                if (storageItem.inputs && Array.isArray(storageItem.inputs)) {
                    for (const input of storageItem.inputs) {
                        if (input.from_ids && Array.isArray(input.from_ids)) {
                            const index = input.from_ids.indexOf(editingResourceNodeId);
                            if (index !== -1) {
                                input.from_ids[index] = nodeId;
                            }
                        }
                    }
                }
            }

            // Update dispatchers
            const dispatchers = factory.dispatchers || {};
            for (const dispatcher of Object.values(dispatchers)) {
                if (dispatcher.from_ids && Array.isArray(dispatcher.from_ids)) {
                    const index = dispatcher.from_ids.indexOf(editingResourceNodeId);
                    if (index !== -1) {
                        dispatcher.from_ids[index] = nodeId;
                    }
                }
            }
        }
    }

    pins[selectedPinId].resource_nodes[nodeId] = nodeData;

    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resource_nodes: pins[selectedPinId].resource_nodes,
                factories: pins[selectedPinId].factories
            })
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

    // Remove references to this resource node from all from_ids in all factories of this site
    removeFromIdsReference(editingResourceNodeId, selectedPinId);

    delete pins[selectedPinId].resource_nodes[editingResourceNodeId];

    try {
        const response = await fetch(`/api/pins/${selectedPinId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_nodes: pins[selectedPinId].resource_nodes, factories: pins[selectedPinId].factories })
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
    coreId.focus()
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
    factoryId.focus()
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
        machines: existingFactory && existingFactory.machines ? existingFactory.machines : {},
        dispatchers: existingFactory && existingFactory.dispatchers ? existingFactory.dispatchers : {},
        receivers: existingFactory && existingFactory.receivers ? existingFactory.receivers : {}
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

    // Create badges container
    const fromIdsBadgesContainer = document.createElement('div');
    fromIdsBadgesContainer.className = 'crafter-from-ids-badges';
    fromIdsBadgesContainer.style.display = 'flex';
    fromIdsBadgesContainer.style.flexWrap = 'wrap';
    fromIdsBadgesContainer.style.gap = '8px';
    fromIdsBadgesContainer.style.padding = '12px';
    fromIdsBadgesContainer.style.backgroundColor = '#2a2a2a';
    fromIdsBadgesContainer.style.borderRadius = '4px';
    fromIdsBadgesContainer.style.border = '1px solid #444';
    fromIdsBadgesContainer.style.minHeight = '20px';
    fromIdsBadgesContainer.dataset.value = Array.isArray(inputData.from_ids)
        ? JSON.stringify(inputData.from_ids)
        : (inputData.from_ids ? JSON.stringify(inputData.from_ids.split(', ')) : JSON.stringify([]));

    // Populate badges from input data
    const fromIds = Array.isArray(inputData.from_ids)
        ? inputData.from_ids
        : (inputData.from_ids ? inputData.from_ids.split(/,\s*/) : []);

    fromIds.forEach(id => {
        if (id.trim()) {
            const badge = document.createElement('span');
            badge.className = 'from-id-badge';
            badge.textContent = id.trim();
            badge.style.display = 'inline-block';
            badge.style.padding = '6px 12px';
            badge.style.backgroundColor = '#3a4a6a';
            badge.style.border = '1px solid #5568d3';
            badge.style.borderRadius = '20px';
            badge.style.color = '#e0e0e0';
            badge.style.fontSize = '12px';
            fromIdsBadgesContainer.appendChild(badge);
        }
    });

    const selectSourcesBtn = document.createElement('button');
    selectSourcesBtn.type = 'button';
    selectSourcesBtn.className = 'btn btn-secondary crafter-select-sources-btn';
    selectSourcesBtn.textContent = 'Select Sources';
    selectSourcesBtn.style.marginTop = '8px';
    selectSourcesBtn.style.width = '100%';
    selectSourcesBtn.dataset.inputItem = inputItem;
    selectSourcesBtn.dataset.badgesContainer = '';

    fromIdsField.appendChild(fromIdsLabel);
    fromIdsField.appendChild(fromIdsBadgesContainer);
    fromIdsField.appendChild(selectSourcesBtn);

    const rateField = document.createElement('div');
    rateField.className = 'crafter-input-field';
    const rateLabel = document.createElement('label');
    rateLabel.textContent = 'Rate Limit IPM';
    const rateInput = document.createElement('input');
    rateInput.type = 'number';
    rateInput.className = 'crafter-input-rate';
    rateInput.min = '1';
    rateInput.value = inputData.rate_limit_ipm || 120;
    rateField.appendChild(rateLabel);
    rateField.appendChild(rateInput);

    row.appendChild(itemField);
    row.appendChild(fromIdsField);
    row.appendChild(rateField);

    // Store badge container reference
    selectSourcesBtn.dataset.badgesContainer = fromIdsBadgesContainer.className;
    row.badgesContainer = fromIdsBadgesContainer;

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
    duplicateCrafterBtn.style.display = 'none';
    deleteCrafterBtn.style.display = 'none';
    crafterModal.classList.add('show');
    crafterId.focus()
}

function openEditCrafterModal(pinId, factoryId, machineId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingCrafterId = machineId;
    const crafter = pins[pinId].factories[factoryId].machines.crafters[machineId];

    crafterModalTitle.textContent = 'Edit Crafter';
    crafterId.value = machineId;
    crafterId.disabled = false;
    crafterItem.value = crafter.crafted_item || '';

    // Populate inputs from recipe with existing data
    populateInputsFromRecipeAndData(crafter.crafted_item, crafter.inputs);

    populateCrafterCoreOptions(pinId, crafter.core_id || '');
    duplicateCrafterBtn.style.display = 'inline-block';
    deleteCrafterBtn.style.display = 'block';
    crafterModal.classList.add('show');
}

function handleDuplicateCrafter() {
    if (!selectedPinId || !selectedFactoryId) return;

    // Switch to add mode while keeping all existing details
    editingCrafterId = null;
    crafterModalTitle.textContent = 'Add Crafter';
    crafterId.disabled = false;
    duplicateCrafterBtn.style.display = 'none';
    deleteCrafterBtn.style.display = 'none';
    crafterId.focus();
    crafterId.select();
}

function closeCrafterModal() {
    crafterModal.classList.remove('show');
    editingCrafterId = null;
    selectedFactoryId = null;
    duplicateCrafterBtn.style.display = 'none';
}

function parseCrafterInputs() {
    const rows = Array.from(crafterInputsContainer.querySelectorAll('.crafter-input-row'));
    const inputs = [];

    for (const row of rows) {
        const inputItemElement = row.querySelector('.crafter-input-item');
        const inputItem = inputItemElement.dataset.value || inputItemElement.textContent.trim();
        const badgesContainer = row.querySelector('.crafter-from-ids-badges');
        const rateValue = row.querySelector('.crafter-input-rate').value.trim();

        if (!inputItem) {
            return { error: 'Each input row must include an input item' };
        }

        const rate = parseInt(rateValue);
        if (isNaN(rate) || rate < 1) {
            return { error: 'Each input row must include a positive rate_limit_ipm' };
        }

        // Extract from_ids from badges
        const badges = Array.from(badgesContainer.querySelectorAll('.from-id-badge'));
        const fromIds = badges.map(badge => badge.textContent.trim()).filter(id => id);

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

let currentSelectSourcesButton = null;

function buildCrafterSourcesList(inputItem) {
    const sources = [];
    const inputItemLower = inputItem.toLowerCase();

    const pin = pins[selectedPinId];
    if (!pin) return sources;

    // Add resource nodes with matching item
    if (pin.resource_nodes) {
        for (const [resId, resNode] of Object.entries(pin.resource_nodes)) {
            if (resNode.resource_item.toLowerCase() === inputItemLower) {
                sources.push({
                    fromId: resId,
                    item: resNode.resource_item,
                    rateIpm: resNode.rate_ipm,
                    building: resNode.building || '',
                    type: 'resource'
                });
            }
        }
    }

    // Add crafters with matching item from current factory
    const factory = pin.factories[selectedFactoryId];
    if (factory && factory.machines && factory.machines.crafters) {
        for (const [crafterId, crafter] of Object.entries(factory.machines.crafters)) {
            if (crafter.crafted_item.toLowerCase() === inputItemLower) {
                // Look up building and items_per_minute from item_definitions
                let building = '';
                let rateIpm = '';
                if (window.itemDefinitions) {
                    const itemDef = window.itemDefinitions.find(item =>
                        item.item_name.toLowerCase() === crafter.crafted_item.toLowerCase()
                    );
                    if (itemDef) {
                        building = itemDef.factory || '';
                        rateIpm = itemDef.items_per_minute || '';
                    }
                }
                sources.push({
                    fromId: crafterId,
                    item: crafter.crafted_item,
                    rateIpm: rateIpm,
                    building: building,
                    type: 'crafter'
                });
            }
        }
    }

    // Add storage with matching item or "*"
    if (factory && factory.machines && factory.machines.storage) {
        for (const [storageId, storage] of Object.entries(factory.machines.storage)) {
            if (storage.stored_item === '*' || storage.stored_item.toLowerCase() === inputItemLower) {
                sources.push({
                    fromId: storageId,
                    item: storage.stored_item,
                    rateIpm: '',
                    building: storage.building_id || '',
                    type: 'storage'
                });
            }
        }
    }

    // Add receivers with matching dispatcher item
    if (factory && factory.receivers) {
        for (const [receiverId, receiver] of Object.entries(factory.receivers)) {
            if (receiver.site_id && receiver.factory_id && receiver.dispatcher_id) {
                const dispatcherPin = pins[receiver.site_id];
                if (dispatcherPin && dispatcherPin.factories && dispatcherPin.factories[receiver.factory_id]) {
                    const dispatcherFactory = dispatcherPin.factories[receiver.factory_id];
                    if (dispatcherFactory.dispatchers && dispatcherFactory.dispatchers[receiver.dispatcher_id]) {
                        const dispatcher = dispatcherFactory.dispatchers[receiver.dispatcher_id];
                        const dispatchedItem = dispatcher.dipatched_item || dispatcher.dispatched_item || '';
                        if (dispatchedItem.toLowerCase() === inputItemLower) {
                            sources.push({
                                fromId: receiverId,
                                item: dispatchedItem,
                                rateIpm: '',
                                building: receiver.building_id || '',
                                type: 'receiver'
                            });
                        }
                    }
                }
            }
        }
    }

    // Sort by fromId
    sources.sort((a, b) => a.fromId.localeCompare(b.fromId));

    return sources;
}

function populateCrafterSourcesTable(inputItem) {
    const tbody = crafterSourcesSelectionTable.querySelector('tbody');
    tbody.innerHTML = '';

    const sources = buildCrafterSourcesList(inputItem);

    sources.forEach((source, index) => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #555';
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#404040';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });

        const checkboxCell = document.createElement('td');
        checkboxCell.style.border = '1px solid #555';
        checkboxCell.style.padding = '10px';
        checkboxCell.style.textAlign = 'center';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = source.fromId;
        checkbox.className = 'source-checkbox';
        checkbox.dataset.sourceIndex = index;
        checkboxCell.appendChild(checkbox);

        const fromIdCell = document.createElement('td');
        fromIdCell.style.border = '1px solid #555';
        fromIdCell.style.padding = '10px';
        fromIdCell.textContent = source.fromId;

        const itemCell = document.createElement('td');
        itemCell.style.border = '1px solid #555';
        itemCell.style.padding = '10px';
        itemCell.textContent = source.item;

        const rateCell = document.createElement('td');
        rateCell.style.border = '1px solid #555';
        rateCell.style.padding = '10px';
        rateCell.style.textAlign = 'right';
        rateCell.textContent = source.rateIpm ? source.rateIpm : '';

        const buildingCell = document.createElement('td');
        buildingCell.style.border = '1px solid #555';
        buildingCell.style.padding = '10px';
        buildingCell.textContent = source.building;

        row.appendChild(checkboxCell);
        row.appendChild(fromIdCell);
        row.appendChild(itemCell);
        row.appendChild(rateCell);
        row.appendChild(buildingCell);
        tbody.appendChild(row);
    });
}

function openSelectCrafterSourcesModal(button) {
    currentSelectSourcesButton = button;
    const inputItem = button.dataset.inputItem;

    populateCrafterSourcesTable(inputItem);
    selectAllSourcesCheckbox.checked = false;
    selectCrafterSourcesModal.classList.add('show');
}

function closeSelectCrafterSourcesModal() {
    selectCrafterSourcesModal.classList.remove('show');
    currentSelectSourcesButton = null;
}

function handleSelectAllSources(event) {
    const checkboxes = Array.from(crafterSourcesSelectionTable.querySelectorAll('.source-checkbox'));
    checkboxes.forEach(checkbox => {
        checkbox.checked = event.target.checked;
    });
}

function handleSelectSources() {
    const checkboxes = Array.from(crafterSourcesSelectionTable.querySelectorAll('.source-checkbox:checked'));
    const selectedIds = checkboxes.map(checkbox => checkbox.value);

    if (currentSelectSourcesButton && currentSelectSourcesButton.parentElement) {
        // Find the badges container in the same input row
        const row = currentSelectSourcesButton.closest('.crafter-input-row');
        if (row) {
            const badgesContainer = row.querySelector('.crafter-from-ids-badges');
            if (badgesContainer) {
                // Clear existing badges
                badgesContainer.innerHTML = '';

                // Add new badges
                selectedIds.forEach(id => {
                    const badge = document.createElement('span');
                    badge.className = 'from-id-badge';
                    badge.textContent = id;
                    badge.style.display = 'inline-block';
                    badge.style.padding = '6px 12px';
                    badge.style.backgroundColor = '#3a4a6a';
                    badge.style.border = '1px solid #5568d3';
                    badge.style.borderRadius = '20px';
                    badge.style.color = '#e0e0e0';
                    badge.style.fontSize = '12px';
                    badgesContainer.appendChild(badge);
                });
            }
        }
    }

    closeSelectCrafterSourcesModal();
}

let currentSelectStorageSourcesButton = null;

function buildStorageSourcesList(storedItem, excludeStorageId = null) {
    const sources = [];

    const pin = pins[selectedPinId];
    if (!pin) return sources;

    const factory = pin.factories[selectedFactoryId];
    if (!factory) return sources;

    // If stored item is "*", return all possible sources; otherwise match by item
    const storedItemLower = storedItem.toLowerCase();
    const matchAny = storedItem === '*';

    // Add resource nodes (match only if stored_item matches or is "*")
    if (pin.resource_nodes) {
        for (const [resId, resNode] of Object.entries(pin.resource_nodes)) {
            if (matchAny || resNode.resource_item.toLowerCase() === storedItemLower) {
                sources.push({
                    fromId: resId,
                    item: resNode.resource_item,
                    building: resNode.building || '',
                    type: 'resource'
                });
            }
        }
    }

    // Add crafters (match only if stored_item matches or is "*")
    if (factory.machines && factory.machines.crafters) {
        for (const [crafterId, crafter] of Object.entries(factory.machines.crafters)) {
            if (matchAny || crafter.crafted_item.toLowerCase() === storedItemLower) {
                let building = '';
                if (window.itemDefinitions) {
                    const itemDef = window.itemDefinitions.find(item =>
                        item.item_name.toLowerCase() === crafter.crafted_item.toLowerCase()
                    );
                    if (itemDef) {
                        building = itemDef.factory || '';
                    }
                }
                sources.push({
                    fromId: crafterId,
                    item: crafter.crafted_item,
                    building: building,
                    type: 'crafter'
                });
            }
        }
    }

    // Add storage (match only if stored_item matches or is "*", and exclude self)
    if (factory.machines && factory.machines.storage) {
        for (const [storageId, storage] of Object.entries(factory.machines.storage)) {
            if (storageId === excludeStorageId) continue; // Skip self
            if (matchAny || storage.stored_item === '*' || storage.stored_item.toLowerCase() === storedItemLower) {
                sources.push({
                    fromId: storageId,
                    item: storage.stored_item,
                    building: storage.building_id || '',
                    type: 'storage'
                });
            }
        }
    }

    // Add receivers (match dispatcher item, or all if stored_item is "*")
    if (factory.receivers) {
        for (const [receiverId, receiver] of Object.entries(factory.receivers)) {
            if (receiver.site_id && receiver.factory_id && receiver.dispatcher_id) {
                const dispatcherPin = pins[receiver.site_id];
                if (dispatcherPin && dispatcherPin.factories && dispatcherPin.factories[receiver.factory_id]) {
                    const dispatcherFactory = dispatcherPin.factories[receiver.factory_id];
                    if (dispatcherFactory.dispatchers && dispatcherFactory.dispatchers[receiver.dispatcher_id]) {
                        const dispatcher = dispatcherFactory.dispatchers[receiver.dispatcher_id];
                        const dispatchedItem = dispatcher.dipatched_item || dispatcher.dispatched_item || '';
                        if (matchAny || dispatchedItem.toLowerCase() === storedItemLower) {
                            sources.push({
                                fromId: receiverId,
                                item: dispatchedItem,
                                building: receiver.building_id || '',
                                type: 'receiver'
                            });
                        }
                    }
                }
            }
        }
    }

    // Sort by fromId
    sources.sort((a, b) => a.fromId.localeCompare(b.fromId));

    return sources;
}

function populateStorageSourcesTable(storedItem, excludeStorageId = null) {
    const tbody = document.querySelector('#storageSourcesSelectionTable tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    const sources = buildStorageSourcesList(storedItem, excludeStorageId);

    sources.forEach((source, index) => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #555';
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#404040';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });

        const checkboxCell = document.createElement('td');
        checkboxCell.style.border = '1px solid #555';
        checkboxCell.style.padding = '10px';
        checkboxCell.style.textAlign = 'center';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = source.fromId;
        checkbox.className = 'storage-source-checkbox';
        checkbox.dataset.sourceIndex = index;
        checkboxCell.appendChild(checkbox);

        const fromIdCell = document.createElement('td');
        fromIdCell.style.border = '1px solid #555';
        fromIdCell.style.padding = '10px';
        fromIdCell.textContent = source.fromId;

        const itemCell = document.createElement('td');
        itemCell.style.border = '1px solid #555';
        itemCell.style.padding = '10px';
        itemCell.textContent = source.item;

        const buildingCell = document.createElement('td');
        buildingCell.style.border = '1px solid #555';
        buildingCell.style.padding = '10px';
        buildingCell.textContent = source.building;

        row.appendChild(checkboxCell);
        row.appendChild(fromIdCell);
        row.appendChild(itemCell);
        row.appendChild(buildingCell);
        tbody.appendChild(row);
    });
}

function openSelectStorageSourcesModal(button) {
    currentSelectStorageSourcesButton = button;
    const row = button.closest('.storage-input-row');
    if (!row) return;

    // Get the stored item from the storage modal
    const storedItem = storageStoredItem.value || '*';

    // Pass the current storage ID to exclude it from the list
    populateStorageSourcesTable(storedItem, editingStorageId);

    const selectAllCheckbox = document.querySelector('#selectAllStorageSourcesCheckbox');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
    }

    const modal = document.getElementById('selectStorageSourcesModal');
    if (modal) {
        modal.classList.add('show');
    }
}

function closeSelectStorageSourcesModal() {
    const modal = document.getElementById('selectStorageSourcesModal');
    if (modal) {
        modal.classList.remove('show');
    }
    currentSelectStorageSourcesButton = null;
}

function handleSelectAllStorageSources(event) {
    const checkboxes = Array.from(document.querySelectorAll('#storageSourcesSelectionTable .storage-source-checkbox'));
    checkboxes.forEach(checkbox => {
        checkbox.checked = event.target.checked;
    });
}

function handleSelectStorageSources() {
    const checkboxes = Array.from(document.querySelectorAll('#storageSourcesSelectionTable .storage-source-checkbox:checked'));
    const selectedIds = checkboxes.map(checkbox => checkbox.value);

    if (currentSelectStorageSourcesButton && currentSelectStorageSourcesButton.closest('.storage-input-row')) {
        const row = currentSelectStorageSourcesButton.closest('.storage-input-row');
        if (row) {
            const badgesContainer = row.querySelector('.storage-from-ids-badges');
            if (badgesContainer) {
                // Clear existing badges
                badgesContainer.innerHTML = '';

                // Add new badges
                selectedIds.forEach(id => {
                    const badge = document.createElement('span');
                    badge.className = 'from-id-badge';
                    badge.textContent = id;
                    badge.style.display = 'inline-block';
                    badge.style.padding = '6px 12px';
                    badge.style.backgroundColor = '#3a4a6a';
                    badge.style.border = '1px solid #5568d3';
                    badge.style.borderRadius = '20px';
                    badge.style.color = '#e0e0e0';
                    badge.style.fontSize = '12px';
                    badgesContainer.appendChild(badge);
                });
            }
        }
    }

    closeSelectStorageSourcesModal();
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

    // Check for duplicate ID (allow current ID when editing)
    if (pins[selectedPinId].factories[selectedFactoryId].machines.crafters[machineId]) {
        if (!editingCrafterId || editingCrafterId !== machineId) {
            alert('A crafter with this ID already exists');
            return;
        }
    }

    const pin = pins[selectedPinId];
    if (pin.resource_nodes && pin.resource_nodes[machineId]) {
        alert('This ID is already used by a resource node in this site');
        return;
    }

    const factory = pin.factories[selectedFactoryId];
    const exclude = (editingCrafterId && editingCrafterId === machineId)
        ? { type: 'crafter', id: editingCrafterId }
        : null;
    const conflicts = getFactoryIdConflicts(factory, machineId, exclude);
    if (conflicts.length > 0) {
        alert(`This ID is already used by ${conflicts.join(', ')} in this factory`);
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

    // If editing and ID changed, delete old entry and update all from_ids references
    if (editingCrafterId && editingCrafterId !== machineId) {
        delete pins[selectedPinId].factories[selectedFactoryId].machines.crafters[editingCrafterId];

        // Update all from_ids references in this factory
        const factory = pins[selectedPinId].factories[selectedFactoryId];

        // Update crafters
        const crafters = factory.machines?.crafters || {};
        for (const crafter of Object.values(crafters)) {
            if (crafter.inputs && Array.isArray(crafter.inputs)) {
                for (const input of crafter.inputs) {
                    if (input.from_ids && Array.isArray(input.from_ids)) {
                        const index = input.from_ids.indexOf(editingCrafterId);
                        if (index !== -1) {
                            input.from_ids[index] = machineId;
                        }
                    }
                }
            }
        }

        // Update storage
        const storage = factory.machines?.storage || {};
        for (const storageItem of Object.values(storage)) {
            if (storageItem.inputs && Array.isArray(storageItem.inputs)) {
                for (const input of storageItem.inputs) {
                    if (input.from_ids && Array.isArray(input.from_ids)) {
                        const index = input.from_ids.indexOf(editingCrafterId);
                        if (index !== -1) {
                            input.from_ids[index] = machineId;
                        }
                    }
                }
            }
        }

        // Update dispatchers
        const dispatchers = factory.dispatchers || {};
        for (const dispatcher of Object.values(dispatchers)) {
            if (dispatcher.from_ids && Array.isArray(dispatcher.from_ids)) {
                const index = dispatcher.from_ids.indexOf(editingCrafterId);
                if (index !== -1) {
                    dispatcher.from_ids[index] = machineId;
                }
            }
        }
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

    // Remove references to this crafter from all from_ids in this factory
    removeFromIdsReference(editingCrafterId, selectedPinId, selectedFactoryId);

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

    // Create badges container
    const fromIdsBadgesContainer = document.createElement('div');
    fromIdsBadgesContainer.className = 'storage-from-ids-badges';
    fromIdsBadgesContainer.style.display = 'flex';
    fromIdsBadgesContainer.style.flexWrap = 'wrap';
    fromIdsBadgesContainer.style.gap = '8px';
    fromIdsBadgesContainer.style.padding = '12px';
    fromIdsBadgesContainer.style.backgroundColor = '#2a2a2a';
    fromIdsBadgesContainer.style.borderRadius = '4px';
    fromIdsBadgesContainer.style.border = '1px solid #444';
    fromIdsBadgesContainer.style.minHeight = '20px';
    fromIdsBadgesContainer.dataset.value = Array.isArray(inputData.from_ids)
        ? JSON.stringify(inputData.from_ids)
        : (inputData.from_ids ? JSON.stringify(inputData.from_ids.split(', ')) : JSON.stringify([]));

    // Populate badges from input data
    const fromIds = Array.isArray(inputData.from_ids)
        ? inputData.from_ids
        : (inputData.from_ids ? inputData.from_ids.split(/,\s*/) : []);

    fromIds.forEach(id => {
        if (id.trim()) {
            const badge = document.createElement('span');
            badge.className = 'from-id-badge';
            badge.textContent = id.trim();
            badge.style.display = 'inline-block';
            badge.style.padding = '6px 12px';
            badge.style.backgroundColor = '#3a4a6a';
            badge.style.border = '1px solid #5568d3';
            badge.style.borderRadius = '20px';
            badge.style.color = '#e0e0e0';
            badge.style.fontSize = '12px';
            fromIdsBadgesContainer.appendChild(badge);
        }
    });

    const selectSourcesBtn = document.createElement('button');
    selectSourcesBtn.type = 'button';
    selectSourcesBtn.className = 'btn btn-secondary storage-select-sources-btn';
    selectSourcesBtn.textContent = 'Select Sources';
    selectSourcesBtn.style.marginTop = '8px';
    selectSourcesBtn.style.width = '100%';

    fromIdsField.appendChild(fromIdsLabel);
    fromIdsField.appendChild(fromIdsBadgesContainer);
    fromIdsField.appendChild(selectSourcesBtn);

    const rateField = document.createElement('div');
    rateField.className = 'storage-input-field';
    const rateLabel = document.createElement('label');
    rateLabel.textContent = 'Rate Limit IPM';
    const rateInput = document.createElement('input');
    rateInput.type = 'number';
    rateInput.className = 'storage-input-rate';
    rateInput.min = '1';
    rateInput.value = inputData.rate_limit_ipm || 120;
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

    // Store badge container reference
    row.badgesContainer = fromIdsBadgesContainer;

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
    duplicateStorageBtn.style.display = 'none';
    deleteStorageBtn.style.display = 'none';
    storageModal.classList.add('show');
    storageId.focus()
}

function openEditStorageModal(pinId, factoryId, machineId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingStorageId = machineId;
    const storage = pins[pinId].factories[factoryId].machines.storage[machineId];

    storageModalTitle.textContent = 'Edit Storage';
    storageId.value = machineId;
    storageId.disabled = false;
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
    duplicateStorageBtn.style.display = 'inline-block';
    deleteStorageBtn.style.display = 'block';
    storageModal.classList.add('show');
}

function handleDuplicateStorage() {
    if (!selectedPinId || !selectedFactoryId) return;

    // Switch to add mode while keeping all existing details
    editingStorageId = null;
    storageModalTitle.textContent = 'Add Storage';
    storageId.disabled = false;
    duplicateStorageBtn.style.display = 'none';
    deleteStorageBtn.style.display = 'none';
    storageId.focus();
    storageId.select();
}

function closeStorageModal() {
    storageModal.classList.remove('show');
    editingStorageId = null;
    selectedFactoryId = null;
    duplicateStorageBtn.style.display = 'none';
}

function parseStorageInputs() {
    const rows = Array.from(storageInputsContainer.querySelectorAll('.storage-input-row'));
    const inputs = [];

    for (const row of rows) {
        const rateValue = row.querySelector('.storage-input-rate').value.trim();

        const rate = parseInt(rateValue);
        if (isNaN(rate) || rate < 1) {
            return { error: 'Each input row must include a positive rate_limit_ipm' };
        }

        // Extract from_ids from badges container
        const badgesContainer = row.querySelector('.storage-from-ids-badges');
        const fromIds = [];
        if (badgesContainer) {
            const badges = badgesContainer.querySelectorAll('.from-id-badge');
            badges.forEach(badge => {
                fromIds.push(badge.textContent.trim());
            });
        }

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

    const pin = pins[selectedPinId];
    if (pin.resource_nodes && pin.resource_nodes[machineId]) {
        alert('This ID is already used by a resource node in this site');
        return;
    }

    const factory = pin.factories[selectedFactoryId];
    const exclude = (editingStorageId && editingStorageId === machineId)
        ? { type: 'storage', id: editingStorageId }
        : null;
    const conflicts = getFactoryIdConflicts(factory, machineId, exclude);
    if (conflicts.length > 0) {
        alert(`This ID is already used by ${conflicts.join(', ')} in this factory`);
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

        // Update all from_ids references in this factory
        const factory = pins[selectedPinId].factories[selectedFactoryId];

        // Update crafters
        const crafters = factory.machines?.crafters || {};
        for (const crafter of Object.values(crafters)) {
            if (crafter.inputs && Array.isArray(crafter.inputs)) {
                for (const input of crafter.inputs) {
                    if (input.from_ids && Array.isArray(input.from_ids)) {
                        const index = input.from_ids.indexOf(editingStorageId);
                        if (index !== -1) {
                            input.from_ids[index] = machineId;
                        }
                    }
                }
            }
        }

        // Update storage
        const storage = factory.machines?.storage || {};
        for (const storageItem of Object.values(storage)) {
            if (storageItem.inputs && Array.isArray(storageItem.inputs)) {
                for (const input of storageItem.inputs) {
                    if (input.from_ids && Array.isArray(input.from_ids)) {
                        const index = input.from_ids.indexOf(editingStorageId);
                        if (index !== -1) {
                            input.from_ids[index] = machineId;
                        }
                    }
                }
            }
        }

        // Update dispatchers
        const dispatchers = factory.dispatchers || {};
        for (const dispatcher of Object.values(dispatchers)) {
            if (dispatcher.from_ids && Array.isArray(dispatcher.from_ids)) {
                const index = dispatcher.from_ids.indexOf(editingStorageId);
                if (index !== -1) {
                    dispatcher.from_ids[index] = machineId;
                }
            }
        }
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

    // Remove references to this storage from all from_ids in this factory
    removeFromIdsReference(editingStorageId, selectedPinId, selectedFactoryId);

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

function setReceiverDispatcherLabels(selection) {
    const siteValue = selection ? selection.site_id : '';
    const factoryValue = selection ? selection.factory_id : '';
    const dispatcherValue = selection ? selection.dispatcher_id : '';

    receiverSiteLabel.textContent = siteValue || '-';
    receiverFactoryLabel.textContent = factoryValue || '-';
    receiverDispatcherLabel.textContent = dispatcherValue || '-';
}

function buildReceiverDispatcherList() {
    const list = [];

    for (const [siteId, pin] of Object.entries(pins || {})) {
        if (!pin.factories) continue;
        for (const [factoryId, factory] of Object.entries(pin.factories)) {
            // May not receive items from dispatchers of the same factory.
            if (selectedPinId === siteId && selectedFactoryId === factoryId) continue;
            if (!factory.dispatchers) continue;
            for (const [dispatcherId, dispatcher] of Object.entries(factory.dispatchers)) {
                const item = dispatcher.dipatched_item || dispatcher.dispatched_item || '';
                list.push({
                    item,
                    site_id: siteId,
                    factory_id: factoryId,
                    dispatcher_id: dispatcherId
                });
            }
        }
    }

    list.sort((a, b) => {
        const itemCompare = a.item.localeCompare(b.item);
        if (itemCompare !== 0) return itemCompare;
        const siteCompare = a.site_id.localeCompare(b.site_id);
        if (siteCompare !== 0) return siteCompare;
        const factoryCompare = a.factory_id.localeCompare(b.factory_id);
        if (factoryCompare !== 0) return factoryCompare;
        return a.dispatcher_id.localeCompare(b.dispatcher_id);
    });

    return list;
}

function populateReceiverDispatcherTable() {
    const tbody = receiverDispatcherSelectionTable.querySelector('tbody');
    tbody.innerHTML = '';

    const list = buildReceiverDispatcherList();
    list.forEach(entry => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #555';
        row.style.cursor = 'pointer';
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#404040';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });
        row.addEventListener('click', () => {
            selectedReceiverDispatcher = entry;
            setReceiverDispatcherLabels(entry);
            closeSelectReceiverDispatcherModal();
        });

        row.innerHTML = `
            <td style="border: 1px solid #555; padding: 10px;">${entry.item}</td>
            <td style="border: 1px solid #555; padding: 10px;">${entry.site_id}</td>
            <td style="border: 1px solid #555; padding: 10px;">${entry.factory_id}</td>
            <td style="border: 1px solid #555; padding: 10px;">${entry.dispatcher_id}</td>
        `;

        tbody.appendChild(row);
    });
}

function openSelectReceiverDispatcherModal() {
    populateReceiverDispatcherTable();
    selectReceiverDispatcherModal.classList.add('show');
}

function closeSelectReceiverDispatcherModal() {
    selectReceiverDispatcherModal.classList.remove('show');

    receiverId.focus()
}

function openAddReceiverModal(pinId, factoryId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingReceiverId = null;
    selectedReceiverDispatcher = null;
    receiverModalTitle.textContent = 'Add Receiver';
    receiverId.value = '';
    receiverId.disabled = false;
    setReceiverDispatcherLabels(null);
    receiverBuildingId.value = '';
    receiverCoreGroup.style.display = 'none';
    receiverCoreId.value = '';
    deleteReceiverBtn.style.display = 'none';
    receiverModal.classList.add('show');
    openSelectReceiverDispatcherModal();
}

function openEditReceiverModal(pinId, factoryId, recId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingReceiverId = recId;
    const receiver = pins[pinId].factories[factoryId].receivers[recId];

    receiverModalTitle.textContent = 'Edit Receiver';
    receiverId.value = recId;
    receiverId.disabled = false;
    selectedReceiverDispatcher = {
        site_id: receiver.site_id || '',
        factory_id: receiver.factory_id || '',
        dispatcher_id: receiver.dispatcher_id || '',
        item: ''
    };
    setReceiverDispatcherLabels(selectedReceiverDispatcher);
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

    if (!selectedReceiverDispatcher || !selectedReceiverDispatcher.site_id || !selectedReceiverDispatcher.factory_id || !selectedReceiverDispatcher.dispatcher_id) {
        alert('Please select a dispatcher');
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

    const pin = pins[selectedPinId];
    if (pin.resource_nodes && pin.resource_nodes[recId]) {
        alert('This ID is already used by a resource node in this site');
        return;
    }

    const factory = pin.factories[selectedFactoryId];
    const exclude = (editingReceiverId && editingReceiverId === recId)
        ? { type: 'receiver', id: editingReceiverId }
        : null;
    const conflicts = getFactoryIdConflicts(factory, recId, exclude);
    if (conflicts.length > 0) {
        alert(`This ID is already used by ${conflicts.join(', ')} in this factory`);
        return;
    }

    const receiverData = {
        site_id: selectedReceiverDispatcher.site_id,
        factory_id: selectedReceiverDispatcher.factory_id,
        dispatcher_id: selectedReceiverDispatcher.dispatcher_id,
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

    // If editing and ID changed, delete old entry and update all from_ids references
    if (editingReceiverId && editingReceiverId !== recId) {
        delete pins[selectedPinId].factories[selectedFactoryId].receivers[editingReceiverId];

        // Update all from_ids references in this factory
        const factory = pins[selectedPinId].factories[selectedFactoryId];

        // Update crafters
        const crafters = factory.machines?.crafters || {};
        for (const crafter of Object.values(crafters)) {
            if (crafter.inputs && Array.isArray(crafter.inputs)) {
                for (const input of crafter.inputs) {
                    if (input.from_ids && Array.isArray(input.from_ids)) {
                        const index = input.from_ids.indexOf(editingReceiverId);
                        if (index !== -1) {
                            input.from_ids[index] = recId;
                        }
                    }
                }
            }
        }

        // Update storage
        const storage = factory.machines?.storage || {};
        for (const storageItem of Object.values(storage)) {
            if (storageItem.inputs && Array.isArray(storageItem.inputs)) {
                for (const input of storageItem.inputs) {
                    if (input.from_ids && Array.isArray(input.from_ids)) {
                        const index = input.from_ids.indexOf(editingReceiverId);
                        if (index !== -1) {
                            input.from_ids[index] = recId;
                        }
                    }
                }
            }
        }

        // Update dispatchers
        const dispatchers = factory.dispatchers || {};
        for (const dispatcher of Object.values(dispatchers)) {
            if (dispatcher.from_ids && Array.isArray(dispatcher.from_ids)) {
                const index = dispatcher.from_ids.indexOf(editingReceiverId);
                if (index !== -1) {
                    dispatcher.from_ids[index] = recId;
                }
            }
        }
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

    // Remove references to this receiver from all from_ids in this factory
    removeFromIdsReference(editingReceiverId, selectedPinId, selectedFactoryId);

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

function setDispatcherFromIdsBadges(fromIds) {
    dispatcherFromIdsBadges.innerHTML = '';
    const ids = Array.isArray(fromIds)
        ? fromIds
        : (fromIds ? fromIds.split(/,\s*/) : []);

    ids.forEach(id => {
        const trimmedId = id.trim();
        if (!trimmedId) return;
        const badge = document.createElement('span');
        badge.className = 'from-id-badge';
        badge.textContent = trimmedId;
        dispatcherFromIdsBadges.appendChild(badge);
    });
}

function buildDispatcherSourcesList(dispatchItem) {
    const sources = [];
    const dispatchItemLower = dispatchItem.toLowerCase();
    const pin = pins[selectedPinId];
    if (!pin) return sources;

    // Resource nodes with matching item
    if (pin.resource_nodes) {
        for (const [resId, resNode] of Object.entries(pin.resource_nodes)) {
            if (resNode.resource_item && resNode.resource_item.toLowerCase() === dispatchItemLower) {
                sources.push({
                    fromId: resId,
                    item: resNode.resource_item,
                    building: resNode.building || '',
                    type: 'resource'
                });
            }
        }
    }

    const factory = pin.factories[selectedFactoryId];

    // Crafters with matching crafted item
    if (factory && factory.machines && factory.machines.crafters) {
        for (const [crafterId, crafter] of Object.entries(factory.machines.crafters)) {
            if (crafter.crafted_item && crafter.crafted_item.toLowerCase() === dispatchItemLower) {
                let building = '';
                if (window.itemDefinitions) {
                    const itemDef = window.itemDefinitions.find(item =>
                        item.item_name.toLowerCase() === crafter.crafted_item.toLowerCase()
                    );
                    if (itemDef) {
                        building = itemDef.factory || '';
                    }
                }
                sources.push({
                    fromId: crafterId,
                    item: crafter.crafted_item,
                    building: building,
                    type: 'crafter'
                });
            }
        }
    }

    // Storage with matching stored item
    if (factory && factory.machines && factory.machines.storage) {
        for (const [storageId, storage] of Object.entries(factory.machines.storage)) {
            if (storage.stored_item && storage.stored_item.toLowerCase() === dispatchItemLower) {
                sources.push({
                    fromId: storageId,
                    item: storage.stored_item,
                    building: storage.building_id || '',
                    type: 'storage'
                });
            }
        }
    }

    sources.sort((a, b) => a.fromId.localeCompare(b.fromId));
    return sources;
}

function populateDispatcherSourcesTable(dispatchItem) {
    const tbody = dispatcherSourcesSelectionTable.querySelector('tbody');
    tbody.innerHTML = '';

    const sources = buildDispatcherSourcesList(dispatchItem);
    sources.forEach((source, index) => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #555';
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#404040';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });

        const checkboxCell = document.createElement('td');
        checkboxCell.style.border = '1px solid #555';
        checkboxCell.style.padding = '10px';
        checkboxCell.style.textAlign = 'center';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = source.fromId;
        checkbox.className = 'dispatcher-source-checkbox';
        checkbox.dataset.sourceIndex = index;
        checkboxCell.appendChild(checkbox);

        const fromIdCell = document.createElement('td');
        fromIdCell.style.border = '1px solid #555';
        fromIdCell.style.padding = '10px';
        fromIdCell.textContent = source.fromId;

        const itemCell = document.createElement('td');
        itemCell.style.border = '1px solid #555';
        itemCell.style.padding = '10px';
        itemCell.textContent = source.item;

        const buildingCell = document.createElement('td');
        buildingCell.style.border = '1px solid #555';
        buildingCell.style.padding = '10px';
        buildingCell.textContent = source.building;

        row.appendChild(checkboxCell);
        row.appendChild(fromIdCell);
        row.appendChild(itemCell);
        row.appendChild(buildingCell);
        tbody.appendChild(row);
    });
}

function openSelectDispatcherSourcesModal() {
    const dispatchItem = dispatchedItem.value.trim();
    if (!dispatchItem) {
        alert('Please select a dispatched item first');
        return;
    }

    populateDispatcherSourcesTable(dispatchItem);
    selectAllDispatcherSourcesCheckbox.checked = false;
    selectDispatcherSourcesModal.classList.add('show');
}

function closeSelectDispatcherSourcesModal() {
    selectDispatcherSourcesModal.classList.remove('show');
}

function handleSelectAllDispatcherSources(event) {
    const checkboxes = Array.from(dispatcherSourcesSelectionTable.querySelectorAll('.dispatcher-source-checkbox'));
    checkboxes.forEach(checkbox => {
        checkbox.checked = event.target.checked;
    });
}

function handleSelectDispatcherSources() {
    const checkboxes = Array.from(dispatcherSourcesSelectionTable.querySelectorAll('.dispatcher-source-checkbox:checked'));
    const selectedIds = checkboxes.map(checkbox => checkbox.value);
    setDispatcherFromIdsBadges(selectedIds);
    closeSelectDispatcherSourcesModal();
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
    dispatcherInputRate.value = '120';
    setDispatcherFromIdsBadges([]);
    dispatcherBuildingId.value = '';
    dispatcherCoreGroup.style.display = 'none';
    dispatcherCoreId.value = '';
    deleteDispatcherBtn.style.display = 'none';
    dispatcherModal.classList.add('show');
    dispatcherId.focus()
}

function openEditDispatcherModal(pinId, factoryId, dispId) {
    selectedPinId = pinId;
    selectedFactoryId = factoryId;
    editingDispatcherId = dispId;
    const dispatcher = pins[pinId].factories[factoryId].dispatchers[dispId];

    dispatcherModalTitle.textContent = 'Edit Dispatcher';
    dispatcherId.value = dispId;
    dispatcherId.disabled = false;
    dispatchedItem.value = dispatcher.dipatched_item || dispatcher.dispatched_item || '';
    dispatcherOutputRate.value = dispatcher.output_rate_limit_ipm || 100;
    dispatcherInputRate.value = dispatcher.input_rate_limit_ipm || 100;
    setDispatcherFromIdsBadges(dispatcher.from_ids || []);
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

    const pin = pins[selectedPinId];
    if (pin.resource_nodes && pin.resource_nodes[dispId]) {
        alert('This ID is already used by a resource node in this site');
        return;
    }

    const factory = pin.factories[selectedFactoryId];
    const exclude = (editingDispatcherId && editingDispatcherId === dispId)
        ? { type: 'dispatcher', id: editingDispatcherId }
        : null;
    const conflicts = getFactoryIdConflicts(factory, dispId, exclude);
    if (conflicts.length > 0) {
        alert(`This ID is already used by ${conflicts.join(', ')} in this factory`);
        return;
    }

    const fromIds = Array.from(dispatcherFromIdsBadges.querySelectorAll('.from-id-badge'))
        .map(badge => badge.textContent.trim())
        .filter(id => id);

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

    // If editing and ID changed, delete old entry and update all receiver references
    if (editingDispatcherId && editingDispatcherId !== dispId) {
        delete pins[selectedPinId].factories[selectedFactoryId].dispatchers[editingDispatcherId];

        // Update all receivers across all sites that reference this dispatcher
        // Receivers identify dispatchers by the combination of site_id, factory_id, and dispatcher_id
        for (const pin of Object.values(pins)) {
            for (const factory of Object.values(pin.factories || {})) {
                const receivers = factory.receivers || {};
                for (const receiver of Object.values(receivers)) {
                    if (receiver.site_id === selectedPinId &&
                        receiver.factory_id === selectedFactoryId &&
                        receiver.dispatcher_id === editingDispatcherId) {
                        receiver.dispatcher_id = dispId;
                    }
                }
            }
        }
    }

    pins[selectedPinId].factories[selectedFactoryId].dispatchers[dispId] = dispatcherData;

    try {
        // Send updates sequentially to avoid concurrent writes to pins_data.json
        for (const pinId of Object.keys(pins)) {
            const response = await fetch(`/api/pins/${pinId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ factories: pins[pinId].factories })
            });
            if (!response.ok) throw new Error(`Failed to update pin ${pinId}`);
            const updatedPin = await response.json();
            pins[pinId] = updatedPin;
        }

        renderPins();
        renderPinsList();
        closeDispatcherModal();
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

            // Reload all pins to reflect cascading receiver deletions across all sites
            await loadPins();

            renderPins();
            renderPinsList();
            closeDispatcherModal();

            const deletedReceivers = updatedPin.deleted_receivers || 0;
            if (deletedReceivers > 0) {
                alert(`Dispatcher deleted. ${deletedReceivers} receiver(s) across all sites referencing this dispatcher were also deleted.`);
            }
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

/*
Instead of getting the visualization data and then creating the page in JavaScript, rather
use the visualization route to have the server render the visualization. This allows for
bookmarking and page refreshes,
*/
function openFactoryVisualizationDirectRender(pinId, factoryId) {
    window.open(
        `/api/pins/${pinId}/${factoryId}/visualization`, 
        `Starrupture Factory Visualization: ${pinId}/${factoryId}` )
}

// Factory Visualization Functions
function renderPopupDocument(targetWindow, title, styles, bodyHtml) {
    if (!targetWindow || targetWindow.closed) return;

    const doc = targetWindow.document;
    const head = doc.head || doc.getElementsByTagName('head')[0];
    const body = doc.body || doc.getElementsByTagName('body')[0];

    if (!head || !body) return;

    doc.title = title;
    head.innerHTML = '';
    body.innerHTML = '';

    const meta = doc.createElement('meta');
    meta.setAttribute('charset', 'UTF-8');
    head.appendChild(meta);

    const styleEl = doc.createElement('style');
    styleEl.textContent = styles;
    head.appendChild(styleEl);

    body.innerHTML = bodyHtml;
}

function openFactoryVisualization(pinId, factoryId) {
    const pin = pins[pinId];
    const factory = pin?.factories?.[factoryId];

    if (!factory) {
        alert('Factory not found');
        return;
    }

    // Open window synchronously from the user click to avoid popup blocking.
    const newWindow = window.open('', '_blank');
    if (!newWindow) {
        alert('Unable to open visualization window. Please allow pop-ups for this site.');
        return;
    }

    renderPopupDocument(
        newWindow,
        'Loading visualization...',
        `
            body {
                font-family: monospace;
                background: #1e1e1e;
                color: #e0e0e0;
                padding: 20px;
                margin: 0;
            }
        `,
        'Generating visualization...'
    );

    // Generate visualization data
    generateFactoryVisualization(pinId, factoryId)
        .then((vizData) => {
            const view = generateVisualizationHTML(
                pinId, factoryId, factory.purpose || 'No purpose set', vizData);

            renderPopupDocument(
                newWindow,
                view.title,
                view.styles,
                view.bodyHtml
            );
        })
        .catch((error) => {
            console.error('Error opening factory visualization:', error);
            if (!newWindow.closed) {
                renderPopupDocument(
                    newWindow,
                    'Visualization Error',
                    `
                        body {
                            font-family: monospace;
                            background: #1e1e1e;
                            color: #e0e0e0;
                            padding: 20px;
                            margin: 0;
                        }
                    `,
                    'Error generating factory visualization.'
                );
            }
            alert('Error generating factory visualization');
        })
}

async function generateFactoryVisualization(pinId, factoryId) {
    const response = await fetch(`/api/pins/${pinId}/${factoryId}/visdata`);
    if (!response.ok) {
        if (404 == response.status) {
            const error = await response.json()
            return {svgStyles: "", svgContent:`<p>${error.error}</p>`}
        }
        
        throw new Error(`Visualization request failed with status ${response.status}`);
    }
    const vizData = await response.json();
    return vizData;
}


function generateVisualizationHTML(pinId, factoryId, purpose, vizData) {

    const styles = `
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
    `;

    return {
        title: `"${pinId}"/"${factoryId}" visualization`,
        styles: `${styles}\n${vizData.svgStyles}`,
        bodyHtml: `
            <div class="container">
                <div class="factory-header">'${pinId}'/'${factoryId}'</div>
                <div class="factory-purpose">${purpose}</div>
                <div class="visualization-wrapper">
                    ${vizData.svgContent}
                </div>
            </div>
        `
    };
}

