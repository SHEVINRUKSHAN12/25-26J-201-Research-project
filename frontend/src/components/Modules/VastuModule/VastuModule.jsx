import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { db } from '../../../firebase';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { ArrowLeft, Compass, Check, SkipForward, Target, Navigation } from 'lucide-react';
import { motion } from 'framer-motion';
import './VastuModule.css';

const DIRECTIONS = [
    { id: 'north', name: 'North', angle: 0, color: '#3b82f6' },
    { id: 'northeast', name: 'North-East', angle: 45, color: '#8b5cf6' },
    { id: 'east', name: 'East', angle: 90, color: '#f59e0b' },
    { id: 'southeast', name: 'South-East', angle: 135, color: '#ef4444' },
    { id: 'south', name: 'South', angle: 180, color: '#ef4444' },
    { id: 'southwest', name: 'South-West', angle: 225, color: '#6b7280' },
    { id: 'west', name: 'West', angle: 270, color: '#10b981' },
    { id: 'northwest', name: 'North-West', angle: 315, color: '#06b6d4' }
];

const VastuModule = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();

    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [facing, setFacing] = useState('north');
    const [entranceDirection, setEntranceDirection] = useState('east');

    useEffect(() => {
        const fetchProject = async () => {
            if (!currentUser) return;
            try {
                const docRef = doc(db, 'projects', id);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    const data = { id: docSnap.id, ...docSnap.data() };
                    setProject(data);
                    if (data.vastuData) {
                        setFacing(data.vastuData.facing || 'north');
                        setEntranceDirection(data.vastuData.entrance || 'east');
                    }
                } else {
                    navigate('/dashboard');
                }
            } catch (error) {
                console.error("Error:", error);
            }
            setLoading(false);
        };
        fetchProject();
    }, [id, currentUser, navigate]);

    const handleSave = async () => {
        try {
            await updateDoc(doc(db, 'projects', id), {
                vastuData: {
                    facing,
                    entrance: entranceDirection,
                    updatedAt: new Date()
                }
            });
        } catch (error) {
            console.error("Error saving:", error);
        }
    };

    const markComplete = async () => {
        await handleSave();
        try {
            await updateDoc(doc(db, 'projects', id), {
                vastuStatus: 'completed',
                interiorStatus: 'active',
                currentStep: 'interior'
            });
            navigate(`/project/${id}`);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    const skip = async () => {
        try {
            await updateDoc(doc(db, 'projects', id), {
                vastuStatus: 'skipped',
                interiorStatus: 'active',
                currentStep: 'interior'
            });
            navigate(`/project/${id}`);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    if (loading) return <div className="loading-screen">Loading Vastu Module...</div>;

    return (
        <div className="vastu-module">
            <header className="vastu-header">
                <button onClick={() => navigate(`/project/${id}`)} className="back-btn">
                    <ArrowLeft size={18} />
                </button>
                <h1><Compass size={24} /> Vastu Check</h1>
                <span className="project-name">{project?.name}</span>
            </header>

            <div className="vastu-content">
                <motion.div
                    className="vastu-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h2>Plot Orientation</h2>
                    <p>Select the direction your plot faces and where the main entrance is located.</p>

                    <div className="direction-section">
                        <h3><Target size={18} /> Plot Facing Direction</h3>
                        <div className="direction-grid">
                            {DIRECTIONS.map(dir => (
                                <div
                                    key={dir.id}
                                    className={`direction-card ${facing === dir.id ? 'selected' : ''}`}
                                    style={{ '--dir-color': dir.color }}
                                    onClick={() => setFacing(dir.id)}
                                >
                                    <Navigation
                                        size={20}
                                        style={{ transform: `rotate(${dir.angle}deg)` }}
                                    />
                                    <span>{dir.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="direction-section">
                        <h3><Navigation size={18} /> Main Entrance Direction</h3>
                        <div className="direction-grid">
                            {DIRECTIONS.map(dir => (
                                <div
                                    key={dir.id}
                                    className={`direction-card ${entranceDirection === dir.id ? 'selected' : ''}`}
                                    style={{ '--dir-color': dir.color }}
                                    onClick={() => setEntranceDirection(dir.id)}
                                >
                                    <Navigation
                                        size={20}
                                        style={{ transform: `rotate(${dir.angle}deg)` }}
                                    />
                                    <span>{dir.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="vastu-result">
                        <h3>Analysis</h3>
                        <p>Based on Vastu principles, your configuration is being analyzed...</p>
                        <div className="result-placeholder">
                            <Compass size={48} />
                            <span>Detailed Vastu analysis coming soon</span>
                        </div>
                    </div>
                </motion.div>

                <div className="vastu-actions">
                    <button className="btn-skip" onClick={skip}>
                        <SkipForward size={18} /> Skip This Step
                    </button>
                    <button className="btn-complete" onClick={markComplete}>
                        <Check size={18} /> Mark Complete
                    </button>
                </div>
            </div>
        </div>
    );
};

export default VastuModule;
