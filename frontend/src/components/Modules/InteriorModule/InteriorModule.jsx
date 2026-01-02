import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { db } from '../../../firebase';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import useImage from 'use-image';
import { Stage, Layer, Rect, Text, Group, Image as KonvaImage, Transformer } from 'react-konva';
import {
    ArrowLeft,
    Save,
    Undo,
    Redo,
    ChevronDown,
    Box,
    Check,
    X,
    Trash2
} from 'lucide-react';
import './InteriorModule.css';



// Import Furniture Catalogs
import bedroomCatalog from '../../../data/interior/catalogs/bedroom_furniture_catalog.json';
import livingRoomCatalog from '../../../data/interior/catalogs/living_room_furniture_catalog.json';
import diningRoomCatalog from '../../../data/interior/catalogs/dining_room_furniture_catalog.json';
import kitchenCatalog from '../../../data/interior/catalogs/kitchen_furniture_catalog.json';
import bathroomCatalog from '../../../data/interior/catalogs/bathroom_furniture_catalog.json';
import apartmentCatalog from '../../../data/interior/catalogs/apartment_furniture_catalog.json';

const CATALOGS = {
    bedroom: bedroomCatalog,
    living_room: livingRoomCatalog,
    dining_room: diningRoomCatalog,
    kitchen: kitchenCatalog,
    bathroom: bathroomCatalog,
    apartment: apartmentCatalog
};

const CATEGORY_ICONS = {
    bed: '🛏️',
    storage: '🗄️',
    table: '🪑',
    seating: '🛋️',
    decor: '💡',
    electronics: '📺',
    sanitary: '🚽',
    appliance: '🍳',
    structural: '🚪'
};

const ROOM_TYPES = [
    { id: 'bedroom', name: 'Bedroom' },
    { id: 'living_room', name: 'Living Room' },
    { id: 'kitchen', name: 'Kitchen' },
    { id: 'bathroom', name: 'Bathroom' },
    { id: 'dining_room', name: 'Dining Room' },
    { id: 'apartment', name: 'Apartment' }
];

// Custom Image Component
const URLImage = ({ src, x, y, width, height, rotation, isSelected, onSelect, onChange }) => {
    const [image] = useImage(src);
    const shapeRef = useRef();

    useEffect(() => {
        if (isSelected) {
            // we need to attach transformer manually
            onSelect({ currentTarget: shapeRef.current });
        }
    }, [isSelected, onSelect]);

    return (
        <Group
            ref={shapeRef}
            x={x}
            y={y}
            rotation={rotation}
            draggable
            onClick={(e) => onSelect(e)}
            onTap={(e) => onSelect(e)}
            onDragEnd={(e) => {
                onChange({
                    x: e.target.x(),
                    y: e.target.y(),
                });
            }}
            onTransformEnd={(e) => {
                const node = shapeRef.current;
                const scaleX = node.scaleX();
                const scaleY = node.scaleY();

                // we will reset it back
                node.scaleX(1);
                node.scaleY(1);

                onChange({
                    x: node.x(),
                    y: node.y(),
                    // set minimal value
                    width: Math.max(5, node.width() * scaleX),
                    height: Math.max(5, node.height() * scaleY),
                    rotation: node.rotation()
                });
            }}
        >
            {image ? (
                <KonvaImage
                    image={image}
                    width={width}
                    height={height}
                    offsetX={width / 2}
                    offsetY={height / 2}
                    stroke={isSelected ? '#3b82f6' : 'transparent'}
                    strokeWidth={isSelected ? 2 : 0}
                />
            ) : (
                <Rect
                    width={width}
                    height={height}
                    fill={isSelected ? '#dbeafe' : '#e2e8f0'}
                    stroke={isSelected ? '#3b82f6' : '#94a3b8'}
                    strokeWidth={isSelected ? 2 : 1}
                    cornerRadius={4}
                    offsetX={width / 2}
                    offsetY={height / 2}
                />
            )}
        </Group>
    );
};

const InteriorModule = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();

    // State
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [viewMode, setViewMode] = useState('2D');
    const [blueprintMode, setBlueprintMode] = useState(false);
    const [activeTab, setActiveTab] = useState('details');
    const [selectedRoom, setSelectedRoom] = useState('bedroom');
    const [roomDropdownOpen, setRoomDropdownOpen] = useState(false);
    const [notification, setNotification] = useState(null);
    const trRef = useRef();

    // Canvas state
    const [furniture, setFurniture] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);

    // Room dimensions
    const [roomWidth, setRoomWidth] = useState(400);
    const [roomHeight, setRoomHeight] = useState(300);
    const canvasWidth = 800;
    const canvasHeight = 500;
    const scale = 100;

    // Per-room state storage
    const [roomStates, setRoomStates] = useState({
        bedroom: { furniture: [], width: 400, height: 300 },
        living_room: { furniture: [], width: 500, height: 400 },
        kitchen: { furniture: [], width: 350, height: 300 },
        bathroom: { furniture: [], width: 250, height: 200 },
        dining_room: { furniture: [], width: 400, height: 350 },
        apartment: { furniture: [], width: 800, height: 600 }
    });

    // Get current catalog
    const currentCatalog = CATALOGS[selectedRoom] || bedroomCatalog;
    const availableFurniture = currentCatalog.furniture || [];

    useEffect(() => {
        const fetchProject = async () => {
            if (!currentUser) return;
            try {
                const docRef = doc(db, 'projects', id);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    const projectData = { id: docSnap.id, ...docSnap.data() };
                    setProject(projectData);

                    if (projectData.interiorData?.rooms) {
                        setRoomStates(projectData.interiorData.rooms);
                        // Load initial room (bedroom) from the saved rooms data
                        const initialRoom = projectData.interiorData.roomType || 'bedroom';
                        const initialData = projectData.interiorData.rooms[initialRoom];
                        if (initialData) {
                            setFurniture(initialData.furniture || []);
                            setRoomWidth(initialData.width || 400);
                            setRoomHeight(initialData.height || 300);
                            setSelectedRoom(initialRoom);
                        }
                    } else if (projectData.interiorData?.furniture) {
                        // Fallback for old data format
                        setFurniture(projectData.interiorData.furniture);
                    }

                    if (!projectData.interiorData?.rooms && projectData.length && projectData.width) {
                        setRoomWidth(parseFloat(projectData.width) * scale);
                        setRoomHeight(parseFloat(projectData.length) * scale);
                    }
                } else {
                    navigate('/dashboard');
                }
            } catch (error) {
                console.error("Error fetching project:", error);
            }
            setLoading(false);
        };

        fetchProject();
    }, [id, currentUser, navigate]);

    // Save current state to roomStates whenever furniture or dimensions change
    useEffect(() => {
        setRoomStates(prev => ({
            ...prev,
            [selectedRoom]: {
                furniture,
                width: roomWidth,
                height: roomHeight
            }
        }));
    }, [furniture, roomWidth, roomHeight, selectedRoom]);

    const handleRoomChange = (newRoomId) => {
        // Load data for the new room
        const nextRoomState = roomStates[newRoomId] || { furniture: [], width: 400, height: 300 };

        setSelectedRoom(newRoomId);
        setFurniture(nextRoomState.furniture || []);
        setRoomWidth(nextRoomState.width || 400);
        setRoomHeight(nextRoomState.height || 300);

        setHistory([]);
        setHistoryIndex(-1);
        setRoomDropdownOpen(false);
    };

    const clearRoom = () => {
        if (window.confirm("Are you sure you want to clear all furniture from this room?")) {
            setFurniture([]);
            setHistory([]);
            setHistoryIndex(-1);
        }
    };

    const addToHistory = (newFurniture) => {
        const newHistory = history.slice(0, historyIndex + 1);
        newHistory.push(newFurniture);
        setHistory(newHistory);
        setHistoryIndex(newHistory.length - 1);
    };

    const undo = () => {
        if (historyIndex > 0) {
            setHistoryIndex(historyIndex - 1);
            setFurniture(history[historyIndex - 1]);
        }
    };

    const redo = () => {
        if (historyIndex < history.length - 1) {
            setHistoryIndex(historyIndex + 1);
            setFurniture(history[historyIndex + 1]);
        }
    };

    const addFurniture = (item) => {
        const pixelWidth = item.width * scale;
        const pixelHeight = item.depth * scale;

        const newFurniture = {
            id: `${item.furniture_id}-${Date.now()}`,
            type: item.furniture_id,
            name: item.label,
            x: roomWidth / 2 + (canvasWidth - roomWidth) / 2,
            y: roomHeight / 2 + (canvasHeight - roomHeight) / 2,
            width: pixelWidth,
            height: pixelHeight,
            rotation: 0,
            icon: CATEGORY_ICONS[item.category] || '📦',
            image_2d: item.image_2d,
            originalHeight: item.height  // Store the actual height from catalog
        };
        const newState = [...furniture, newFurniture];
        setFurniture(newState);
        addToHistory(newState);
    };

    const updateFurniture = (furnitureId, newProps) => {
        const updated = furniture.map(item =>
            item.id === furnitureId ? { ...item, ...newProps } : item
        );
        setFurniture(updated);
    };

    const deleteFurniture = () => {
        if (selectedId) {
            const newFurniture = furniture.filter(item => item.id !== selectedId);
            setFurniture(newFurniture);
            addToHistory(newFurniture);
            setSelectedId(null);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            await updateDoc(doc(db, 'projects', id), {
                interiorData: {
                    rooms: roomStates, // Save all rooms
                    roomType: selectedRoom,
                    updatedAt: new Date()
                }
            });
            setNotification({ type: 'success', message: 'Saved!', details: '' });
            setTimeout(() => setNotification(null), 3000);
        } catch (error) {
            console.error("Error saving:", error);
        }
        setSaving(false);
    };

    const handleOptimize = async () => {
        if (furniture.length === 0) {
            setNotification({ type: 'error', message: 'Please add some furniture first!', details: '' });
            setTimeout(() => setNotification(null), 3000);
            return;
        }

        setIsOptimizing(true);
        try {
            const roomPolygon = [
                [0, 0],
                [roomWidth / scale, 0],
                [roomWidth / scale, roomHeight / scale],
                [0, roomHeight / scale]
            ];

            const furnitureItems = furniture.map(item => ({
                id: item.id,
                width: item.width / scale,
                depth: item.height / scale,
                height: 0,
                rotatable: true,
                category: item.name
            }));

            const response = await fetch('http://localhost:8000/api/v1/interior/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_polygon: roomPolygon,
                    furniture_items: furnitureItems,
                    constraints: {}
                })
            });

            if (!response.ok) throw new Error('Optimization failed');

            const result = await response.json();
            console.log("Optimization Result:", result);

            const optimizedFurniture = result.layout.map(layoutItem => {
                const originalItem = furniture.find(f => f.id === layoutItem.id);
                if (!originalItem) {
                    console.error("Original item not found for ID:", layoutItem.id);
                    return null;
                }
                return {
                    ...originalItem,
                    x: layoutItem.x * scale + (canvasWidth - roomWidth) / 2,
                    y: layoutItem.y * scale + (canvasHeight - roomHeight) / 2,
                    rotation: layoutItem.rotation
                };
            }).filter(item => item !== null);

            console.log("Optimized Furniture State:", optimizedFurniture);

            setFurniture(optimizedFurniture);
            addToHistory(optimizedFurniture);

            setNotification({
                type: 'success',
                message: 'Optimization Complete!',
                details: `Quality Score: ${result.score_percentage}%\nFitness: ${result.fitness.toFixed(2)}`
            });
            setTimeout(() => setNotification(null), 5000);

        } catch (error) {
            console.error("Optimization error:", error);
            setNotification({ type: 'error', message: 'Optimization failed. Ensure backend is running.', details: '' });
            setTimeout(() => setNotification(null), 5000);
        }
        setIsOptimizing(false);
    };

    const markComplete = async () => {
        try {
            await updateDoc(doc(db, 'projects', id), {
                interiorStatus: 'completed',
                exteriorStatus: 'active',
                currentStep: 'exterior'
            });
            navigate(`/project/${id}`);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    const selectedFurniture = furniture.find(f => f.id === selectedId);

    if (loading) return <div className="loading-screen">Loading Interior Module...</div>;

    return (
        <div className="interior-module">
            {/* Header */}
            <header className="interior-header">
                <div className="header-left">
                    <button onClick={() => navigate(`/project/${id}`)} className="back-btn" title="Back to Project">
                        <ArrowLeft size={20} />
                    </button>
                    <h1>Interior Design</h1>
                    <span className="project-name">{project?.name}</span>
                </div>
                <div className="header-right">
                    <div className="view-toggle">
                        <button
                            className={!blueprintMode ? 'active' : ''}
                            onClick={() => setBlueprintMode(false)}
                            title="Realistic View"
                        >
                            🖼️
                        </button>
                        <button
                            className={blueprintMode ? 'active' : ''}
                            onClick={() => setBlueprintMode(true)}
                            title="Blueprint View"
                        >
                            📐
                        </button>
                        <div className="divider" style={{ width: '1px', height: '20px', background: '#334155', margin: '0 10px' }}></div>
                        <button
                            className={viewMode === '2D' ? 'active' : ''}
                            onClick={() => setViewMode('2D')}
                        >
                            2D
                        </button>
                        <button
                            className={viewMode === '3D' ? 'active' : ''}
                            onClick={() => setViewMode('3D')}
                        >
                            3D
                        </button>
                    </div>
                </div>
            </header>

            <div className="interior-layout">
                {/* Sidebar */}
                <aside className="interior-sidebar">
                    {/* Room Selector */}
                    <div className="sidebar-section">
                        <div
                            className="room-selector"
                            onClick={() => setRoomDropdownOpen(!roomDropdownOpen)}
                        >
                            <span>{ROOM_TYPES.find(r => r.id === selectedRoom)?.name}</span>
                            <ChevronDown size={18} />
                        </div>
                        {roomDropdownOpen && (
                            <div className="room-dropdown">
                                {ROOM_TYPES.map(room => (
                                    <div
                                        key={room.id}
                                        className={`room-option ${selectedRoom === room.id ? 'active' : ''}`}
                                        onClick={() => handleRoomChange(room.id)}
                                    >
                                        {room.name}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Room Dimensions Inputs */}
                    <div className="sidebar-section">
                        <h3>ROOM SIZE</h3>
                        <div className="dimensions-panel">
                            <div className="dimension-row">
                                <span className="dimension-label">Width (m)</span>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={(roomWidth / scale).toFixed(1)}
                                    onChange={(e) => setRoomWidth(parseFloat(e.target.value) * scale)}
                                    className="dimension-input"
                                />
                            </div>
                            <div className="dimension-row">
                                <span className="dimension-label">Length (m)</span>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={(roomHeight / scale).toFixed(1)}
                                    onChange={(e) => setRoomHeight(parseFloat(e.target.value) * scale)}
                                    className="dimension-input"
                                />
                            </div>
                            <button className="clear-btn" onClick={clearRoom} style={{ marginTop: '10px', width: '100%', padding: '8px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                                <Trash2 size={14} style={{ marginRight: '5px', verticalAlign: 'middle' }} /> Clear Room
                            </button>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="sidebar-tabs">
                        <button
                            className={activeTab === 'details' ? 'active' : ''}
                            onClick={() => setActiveTab('details')}
                        >
                            DETAILS
                        </button>
                        <button
                            className={activeTab === 'layout' ? 'active' : ''}
                            onClick={() => setActiveTab('layout')}
                        >
                            LAYOUT
                        </button>
                    </div>

                    {/* Furniture Palette */}
                    <div className="sidebar-section">
                        <h3>ADD FURNITURE</h3>
                        <div className="furniture-grid">
                            {availableFurniture.map((item) => (
                                <button
                                    key={item.furniture_id}
                                    className="furniture-item"
                                    onClick={() => addFurniture(item)}
                                    title={`${item.label} (${item.width}m x ${item.depth}m)`}
                                >
                                    <span className="furniture-icon">{CATEGORY_ICONS[item.category] || '📦'}</span>
                                    <span className="furniture-name">{item.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Dimensions Panel */}
                    <div className="sidebar-section">
                        <h3>DIMENSIONS</h3>
                        {selectedFurniture ? (
                            <div className="dimensions-panel">
                                <div className="dimension-row">
                                    <span className="dimension-label">Item</span>
                                    <span className="dimension-value">{selectedFurniture.name}</span>
                                </div>
                                <div className="dimension-row">
                                    <span className="dimension-label">Width (m)</span>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={(selectedFurniture.width / scale).toFixed(2)}
                                        onChange={(e) => updateFurniture(selectedId, { width: parseFloat(e.target.value) * scale })}
                                        className="dimension-input"
                                    />
                                </div>
                                <div className="dimension-row">
                                    <span className="dimension-label">Depth (m)</span>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={(selectedFurniture.height / scale).toFixed(2)}
                                        onChange={(e) => updateFurniture(selectedId, { height: parseFloat(e.target.value) * scale })}
                                        className="dimension-input"
                                    />
                                </div>
                                <div className="dimension-row">
                                    <span className="dimension-label">Height (m)</span>
                                    <span className="dimension-value">{selectedFurniture.originalHeight ? selectedFurniture.originalHeight.toFixed(2) : 'N/A'}</span>
                                </div>
                                <div className="dimension-row">
                                    <span className="dimension-label">Rotation (°)</span>
                                    <div style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
                                        <input
                                            type="number"
                                            value={Math.round(selectedFurniture.rotation || 0)}
                                            onChange={(e) => updateFurniture(selectedId, { rotation: parseFloat(e.target.value) })}
                                            className="dimension-input"
                                            style={{ width: '60px' }}
                                        />
                                        <button
                                            onClick={() => updateFurniture(selectedId, { rotation: (selectedFurniture.rotation || 0) + 90 })}
                                            style={{
                                                padding: '4px 8px',
                                                background: '#e2e8f0',
                                                border: '1px solid #cbd5e1',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                fontSize: '12px'
                                            }}
                                            title="Rotate 90°"
                                        >
                                            ↻ 90°
                                        </button>
                                    </div>
                                </div>
                                <button className="delete-btn" onClick={deleteFurniture}>
                                    Remove Item
                                </button>
                            </div>
                        ) : (
                            <p className="no-selection">Select an item to edit dimensions</p>
                        )}
                    </div>
                </aside>

                {/* Canvas Area */}
                <main className="interior-canvas-container">
                    {/* Toolbar */}
                    <div className="canvas-toolbar">
                        <button onClick={undo} disabled={historyIndex <= 0} title="Undo">
                            <Undo size={18} />
                        </button>
                        <button onClick={redo} disabled={historyIndex >= history.length - 1} title="Redo">
                            <Redo size={18} />
                        </button>
                        <div className="toolbar-divider"></div>
                        <button onClick={handleSave} disabled={saving} title="Save">
                            <Save size={18} />
                            {saving ? 'Saving...' : 'Save'}
                        </button>
                    </div>

                    {/* 2D Canvas */}
                    {viewMode === '2D' && (
                        <div className="canvas-wrapper">
                            <Stage
                                width={canvasWidth}
                                height={canvasHeight}
                                onClick={(e) => {
                                    if (e.target === e.target.getStage()) {
                                        setSelectedId(null);
                                        trRef.current.nodes([]);
                                    }
                                }}
                            >
                                <Layer>
                                    {/* Background */}
                                    <Rect
                                        x={0}
                                        y={0}
                                        width={canvasWidth}
                                        height={canvasHeight}
                                        fill="#f8fafc"
                                    />

                                    {/* Room Boundary */}
                                    <Rect
                                        x={(canvasWidth - roomWidth) / 2}
                                        y={(canvasHeight - roomHeight) / 2}
                                        width={roomWidth}
                                        height={roomHeight}
                                        fill="#ffffff"
                                        stroke={blueprintMode ? "#334155" : "#1e293b"}
                                        strokeWidth={blueprintMode ? 20 : 2}
                                    />

                                    {/* Blueprint Dimension Lines */}
                                    {blueprintMode && (
                                        <>
                                            {/* Top Width Line */}
                                            <Group x={(canvasWidth - roomWidth) / 2} y={(canvasHeight - roomHeight) / 2 - 40}>
                                                <Rect width={roomWidth} height={1} fill="#2563eb" />
                                                <Rect x={0} y={-5} width={1} height={11} fill="#2563eb" />
                                                <Rect x={roomWidth} y={-5} width={1} height={11} fill="#2563eb" />
                                                <Text
                                                    x={roomWidth / 2 - 20}
                                                    y={-20}
                                                    text={`${(roomWidth / scale).toFixed(1)} m`}
                                                    fontSize={14}
                                                    fill="#2563eb"
                                                    fontStyle="bold"
                                                />
                                            </Group>

                                            {/* Left Height Line */}
                                            <Group x={(canvasWidth - roomWidth) / 2 - 40} y={(canvasHeight - roomHeight) / 2}>
                                                <Rect width={1} height={roomHeight} fill="#2563eb" />
                                                <Rect x={-5} y={0} width={11} height={1} fill="#2563eb" />
                                                <Rect x={-5} y={roomHeight} width={11} height={1} fill="#2563eb" />
                                                <Text
                                                    x={-35}
                                                    y={roomHeight / 2}
                                                    text={`${(roomHeight / scale).toFixed(1)} m`}
                                                    fontSize={14}
                                                    fill="#2563eb"
                                                    fontStyle="bold"
                                                    rotation={-90}
                                                />
                                            </Group>
                                        </>
                                    )}

                                    {/* Standard Dimensions (Hidden in Blueprint Mode) */}
                                    {!blueprintMode && (
                                        <>
                                            <Text
                                                x={(canvasWidth - roomWidth) / 2 + roomWidth / 2 - 30}
                                                y={(canvasHeight - roomHeight) / 2 - 25}
                                                text={`${(roomWidth / scale).toFixed(1)} m`}
                                                fontSize={14}
                                                fill="#64748b"
                                            />
                                            <Text
                                                x={(canvasWidth + roomWidth) / 2 + 10}
                                                y={canvasHeight / 2 - 7}
                                                text={`${(roomHeight / scale).toFixed(1)} m`}
                                                fontSize={14}
                                                fill="#64748b"
                                            />
                                        </>
                                    )}

                                    {/* Furniture */}
                                    {furniture.map(item => (
                                        <React.Fragment key={item.id}>
                                            {blueprintMode ? (
                                                // Blueprint Style Furniture
                                                <Group
                                                    x={item.x}
                                                    y={item.y}
                                                    rotation={item.rotation}
                                                    draggable
                                                    onClick={(e) => {
                                                        setSelectedId(item.id);
                                                        trRef.current.nodes([e.currentTarget]);
                                                        trRef.current.getLayer().batchDraw();
                                                    }}
                                                    onDragEnd={(e) => {
                                                        updateFurniture(item.id, {
                                                            x: e.target.x(),
                                                            y: e.target.y()
                                                        });
                                                    }}
                                                    onTransformEnd={(e) => {
                                                        const node = e.target;
                                                        const scaleX = node.scaleX();
                                                        const scaleY = node.scaleY();
                                                        node.scaleX(1);
                                                        node.scaleY(1);
                                                        updateFurniture(item.id, {
                                                            x: node.x(),
                                                            y: node.y(),
                                                            width: Math.max(5, node.width() * scaleX),
                                                            height: Math.max(5, node.height() * scaleY),
                                                            rotation: node.rotation()
                                                        });
                                                    }}
                                                >
                                                    <Rect
                                                        width={item.width}
                                                        height={item.height}
                                                        fill="#ffffff"
                                                        stroke="#0f172a"
                                                        strokeWidth={2}
                                                        offsetX={item.width / 2}
                                                        offsetY={item.height / 2}
                                                    />
                                                    {/* Inner Detail Line */}
                                                    <Rect
                                                        width={item.width - 10}
                                                        height={item.height - 10}
                                                        stroke="#94a3b8"
                                                        strokeWidth={1}
                                                        offsetX={(item.width - 10) / 2}
                                                        offsetY={(item.height - 10) / 2}
                                                    />
                                                    <Text
                                                        text={item.name.toUpperCase()}
                                                        fontSize={10}
                                                        fill="#0f172a"
                                                        fontStyle="bold"
                                                        align="center"
                                                        width={item.width}
                                                        offsetX={item.width / 2}
                                                        offsetY={5}
                                                    />
                                                </Group>
                                            ) : (
                                                // Realistic Style Furniture
                                                item.image_2d ? (
                                                    <URLImage
                                                        src={item.image_2d}
                                                        x={item.x}
                                                        y={item.y}
                                                        width={item.width}
                                                        height={item.height}
                                                        rotation={item.rotation}
                                                        isSelected={selectedId === item.id}
                                                        onSelect={(e) => {
                                                            setSelectedId(item.id);
                                                            if (e.currentTarget) {
                                                                trRef.current.nodes([e.currentTarget]);
                                                                trRef.current.getLayer().batchDraw();
                                                            }
                                                        }}
                                                        onChange={(newAttrs) => {
                                                            updateFurniture(item.id, newAttrs);
                                                        }}
                                                    />
                                                ) : (
                                                    <Group
                                                        x={item.x}
                                                        y={item.y}
                                                        rotation={item.rotation}
                                                        draggable
                                                        onClick={(e) => {
                                                            setSelectedId(item.id);
                                                            trRef.current.nodes([e.currentTarget]);
                                                            trRef.current.getLayer().batchDraw();
                                                        }}
                                                        onDragEnd={(e) => {
                                                            updateFurniture(item.id, {
                                                                x: e.target.x(),
                                                                y: e.target.y()
                                                            });
                                                        }}
                                                        onTransformEnd={(e) => {
                                                            const node = e.target;
                                                            const scaleX = node.scaleX();
                                                            const scaleY = node.scaleY();
                                                            node.scaleX(1);
                                                            node.scaleY(1);
                                                            updateFurniture(item.id, {
                                                                x: node.x(),
                                                                y: node.y(),
                                                                width: Math.max(5, node.width() * scaleX),
                                                                height: Math.max(5, node.height() * scaleY),
                                                                rotation: node.rotation()
                                                            });
                                                        }}
                                                    >
                                                        <Rect
                                                            width={item.width}
                                                            height={item.height}
                                                            fill={selectedId === item.id ? '#dbeafe' : '#e2e8f0'}
                                                            stroke={selectedId === item.id ? '#3b82f6' : '#94a3b8'}
                                                            strokeWidth={selectedId === item.id ? 2 : 1}
                                                            cornerRadius={4}
                                                            offsetX={item.width / 2}
                                                            offsetY={item.height / 2}
                                                        />
                                                        <Text
                                                            text={item.name}
                                                            x={-item.width / 2 + 5}
                                                            y={-7}
                                                            fontSize={12}
                                                            fill="#334155"
                                                        />
                                                    </Group>
                                                ))}
                                        </React.Fragment>
                                    ))}
                                    <Transformer ref={trRef} />
                                </Layer>
                            </Stage>
                        </div>
                    )}

                    {/* 3D View Placeholder */}
                    {viewMode === '3D' && (
                        <div className="view-3d-placeholder">
                            <Box size={64} />
                            <h3>3D View Coming Soon</h3>
                            <p>Three.js integration in progress</p>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="canvas-actions">
                        <button className="btn-optimize" onClick={handleOptimize} disabled={isOptimizing}>
                            {isOptimizing ? 'Optimizing...' : '✨ Auto-Optimize Layout'}
                        </button>
                        <button className="btn-complete" onClick={markComplete}>
                            <Check size={18} /> Mark Complete
                        </button>
                    </div>
                </main>
            </div>

            {/* Notification Toast */}
            {notification && (
                <div className={`notification-toast ${notification.type}`}>
                    <div className="notification-content">
                        <h4>{notification.message}</h4>
                        {notification.details && <pre>{notification.details}</pre>}
                    </div>
                    <button onClick={() => setNotification(null)}><X size={16} /></button>
                </div>
            )}
        </div>
    );
};

export default InteriorModule;
