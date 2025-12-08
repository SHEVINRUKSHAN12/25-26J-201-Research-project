import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { db } from '../../../firebase';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { Stage, Layer, Rect, Text, Group, Line, Transformer } from 'react-konva';
import {
    ArrowLeft,
    Save,
    Undo,
    Redo,
    Bed,
    Armchair,
    Lamp,
    Tv,
    Square,
    ChevronDown,
    Grid3X3,
    Box,
    Settings,
    Check
} from 'lucide-react';
import { motion } from 'framer-motion';
import './InteriorModule.css';

// Furniture types with icons and dimensions
const FURNITURE_TYPES = [
    { id: 'bed', name: 'Bed', icon: '🛏️', width: 200, height: 160, category: 'bedroom' },
    { id: 'wardrobe', name: 'Wardrobe', icon: '🪞', width: 60, height: 180, category: 'bedroom' },
    { id: 'side-table', name: 'Side Table', icon: '🪑', width: 50, height: 50, category: 'bedroom' },
    { id: 'chair', name: 'Chair', icon: '💺', width: 50, height: 50, category: 'living' },
    { id: 'dressing-table', name: 'Dressing Table', icon: '🪞', width: 120, height: 50, category: 'bedroom' },
    { id: 'desk', name: 'Desk', icon: '📋', width: 140, height: 70, category: 'office' },
    { id: 'lamp', name: 'Lamp', icon: '💡', width: 30, height: 30, category: 'decor' },
    { id: 'tv-stand', name: 'TV Stand', icon: '📺', width: 150, height: 40, category: 'living' },
    { id: 'shelf', name: 'Shelf', icon: '📚', width: 100, height: 30, category: 'decor' },
    { id: 'sofa', name: 'Sofa', icon: '🛋️', width: 200, height: 80, category: 'living' },
    { id: 'dining-table', name: 'Dining Table', icon: '🍽️', width: 150, height: 90, category: 'dining' },
    { id: 'cabinet', name: 'Cabinet', icon: '🗄️', width: 80, height: 45, category: 'storage' }
];

const ROOM_TYPES = [
    { id: 'bedroom', name: 'Bedroom' },
    { id: 'living', name: 'Living Room' },
    { id: 'kitchen', name: 'Kitchen' },
    { id: 'bathroom', name: 'Bathroom' },
    { id: 'office', name: 'Home Office' },
    { id: 'dining', name: 'Dining Room' }
];

const InteriorModule = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();

    // State
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [viewMode, setViewMode] = useState('2D');
    const [activeTab, setActiveTab] = useState('details');
    const [selectedRoom, setSelectedRoom] = useState('bedroom');
    const [roomDropdownOpen, setRoomDropdownOpen] = useState(false);

    // Canvas state
    const [furniture, setFurniture] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);

    // Room dimensions (in pixels, scaled from meters)
    const [roomWidth, setRoomWidth] = useState(400);
    const [roomHeight, setRoomHeight] = useState(300);
    const canvasWidth = 800;
    const canvasHeight = 500;
    const scale = 33.33; // 1 meter = 33.33 pixels

    useEffect(() => {
        const fetchProject = async () => {
            if (!currentUser) return;
            try {
                const docRef = doc(db, 'projects', id);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    const projectData = { id: docSnap.id, ...docSnap.data() };
                    setProject(projectData);

                    // Load saved furniture if exists
                    if (projectData.interiorData?.furniture) {
                        setFurniture(projectData.interiorData.furniture);
                    }

                    // Set room dimensions from project
                    if (projectData.length && projectData.width) {
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

    const addFurniture = (type) => {
        const newItem = {
            id: `${type.id}-${Date.now()}`,
            type: type.id,
            name: type.name,
            x: 100 + Math.random() * 100,
            y: 100 + Math.random() * 100,
            width: type.width,
            height: type.height,
            rotation: 0
        };

        const newFurniture = [...furniture, newItem];
        setFurniture(newFurniture);
        addToHistory(newFurniture);
        setSelectedId(newItem.id);
    };

    const updateFurniture = (id, newProps) => {
        const updated = furniture.map(item =>
            item.id === id ? { ...item, ...newProps } : item
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
                    furniture,
                    roomType: selectedRoom,
                    updatedAt: new Date()
                }
            });
            // Show success feedback
        } catch (error) {
            console.error("Error saving:", error);
        }
        setSaving(false);
    };

    const handleOptimize = () => {
        // Placeholder for AI optimization
        alert('AI Optimization coming soon! This will auto-arrange furniture for optimal flow.');
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
                    <button onClick={() => navigate(`/project/${id}`)} className="back-btn">
                        <ArrowLeft size={18} />
                    </button>
                    <h1>Interior Design</h1>
                    <span className="project-name">{project?.name}</span>
                </div>
                <div className="header-right">
                    <div className="view-toggle">
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
                                        onClick={() => {
                                            setSelectedRoom(room.id);
                                            setRoomDropdownOpen(false);
                                        }}
                                    >
                                        {room.name}
                                    </div>
                                ))}
                            </div>
                        )}
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
                            {FURNITURE_TYPES.slice(0, 9).map(type => (
                                <div
                                    key={type.id}
                                    className="furniture-item"
                                    onClick={() => addFurniture(type)}
                                    title={type.name}
                                >
                                    <span className="furniture-icon">{type.icon}</span>
                                    <span className="furniture-name">{type.name}</span>
                                </div>
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
                                    <select
                                        value={selectedFurniture.type}
                                        className="dimension-select"
                                        onChange={(e) => {
                                            const newType = FURNITURE_TYPES.find(t => t.id === e.target.value);
                                            if (newType) {
                                                updateFurniture(selectedId, {
                                                    type: newType.id,
                                                    name: newType.name,
                                                    width: newType.width,
                                                    height: newType.height
                                                });
                                            }
                                        }}
                                    >
                                        {FURNITURE_TYPES.map(t => (
                                            <option key={t.id} value={t.id}>{t.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="dimension-row">
                                    <span className="dimension-label">Width</span>
                                    <span className="dimension-value">{(selectedFurniture.width / scale).toFixed(1)} m</span>
                                </div>
                                <div className="dimension-row">
                                    <span className="dimension-label">Depth</span>
                                    <span className="dimension-value">{(selectedFurniture.height / scale).toFixed(1)} m</span>
                                </div>
                                <button
                                    className="delete-btn"
                                    onClick={deleteFurniture}
                                >
                                    Remove Item
                                </button>
                            </div>
                        ) : (
                            <p className="no-selection">Select an item to view dimensions</p>
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

                                    {/* Room */}
                                    <Rect
                                        x={(canvasWidth - roomWidth) / 2}
                                        y={(canvasHeight - roomHeight) / 2}
                                        width={roomWidth}
                                        height={roomHeight}
                                        fill="#ffffff"
                                        stroke="#1e293b"
                                        strokeWidth={2}
                                    />

                                    {/* Room Dimensions */}
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

                                    {/* Furniture */}
                                    {furniture.map(item => (
                                        <Group
                                            key={item.id}
                                            x={item.x}
                                            y={item.y}
                                            rotation={item.rotation}
                                            draggable
                                            onClick={() => setSelectedId(item.id)}
                                            onDragEnd={(e) => {
                                                updateFurniture(item.id, {
                                                    x: e.target.x(),
                                                    y: e.target.y()
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
                                            />
                                            <Text
                                                text={item.name}
                                                x={5}
                                                y={item.height / 2 - 7}
                                                fontSize={12}
                                                fill="#334155"
                                            />
                                        </Group>
                                    ))}
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
                        <button className="btn-optimize" onClick={handleOptimize}>
                            Optimize
                        </button>
                        <button className="btn-complete" onClick={markComplete}>
                            <Check size={18} /> Mark Complete
                        </button>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default InteriorModule;
