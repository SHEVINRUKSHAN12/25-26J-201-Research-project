import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { db } from '../../../firebase';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { ArrowLeft, Trees, Check, ParkingCircle, Flower2, Home } from 'lucide-react';
import { motion } from 'framer-motion';
import './ExteriorModule.css';

const EXTERIOR_FEATURES = [
    { id: 'garden', name: 'Garden', icon: <Flower2 size={24} />, description: 'Landscaping and green spaces' },
    { id: 'parking', name: 'Parking', icon: <ParkingCircle size={24} />, description: 'Vehicle parking area' },
    { id: 'patio', name: 'Patio', icon: <Home size={24} />, description: 'Outdoor living space' },
    { id: 'pathway', name: 'Pathways', icon: <Trees size={24} />, description: 'Walkways and trails' }
];

const ExteriorModule = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();

    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedFeatures, setSelectedFeatures] = useState([]);

    useEffect(() => {
        const fetchProject = async () => {
            if (!currentUser) return;
            try {
                const docRef = doc(db, 'projects', id);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    const data = { id: docSnap.id, ...docSnap.data() };
                    setProject(data);
                    if (data.exteriorData?.features) {
                        setSelectedFeatures(data.exteriorData.features);
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

    const toggleFeature = (featureId) => {
        setSelectedFeatures(prev =>
            prev.includes(featureId)
                ? prev.filter(f => f !== featureId)
                : [...prev, featureId]
        );
    };

    const markComplete = async () => {
        try {
            await updateDoc(doc(db, 'projects', id), {
                exteriorData: {
                    features: selectedFeatures,
                    updatedAt: new Date()
                },
                exteriorStatus: 'completed',
                status: 'completed'
            });
            navigate(`/project/${id}`);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    if (loading) return <div className="loading-screen">Loading Exterior Module...</div>;

    return (
        <div className="exterior-module">
            <header className="exterior-header">
                <button onClick={() => navigate(`/project/${id}`)} className="back-btn">
                    <ArrowLeft size={18} />
                </button>
                <h1><Trees size={24} /> Exterior & Landscape</h1>
                <span className="project-name">{project?.name}</span>
            </header>

            <div className="exterior-content">
                <motion.div
                    className="exterior-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h2>Landscape Planning</h2>
                    <p>Select the exterior features you want to include in your property.</p>

                    <div className="features-grid">
                        {EXTERIOR_FEATURES.map(feature => (
                            <motion.div
                                key={feature.id}
                                className={`feature-card ${selectedFeatures.includes(feature.id) ? 'selected' : ''}`}
                                onClick={() => toggleFeature(feature.id)}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                <div className="feature-icon">{feature.icon}</div>
                                <h3>{feature.name}</h3>
                                <p>{feature.description}</p>
                                {selectedFeatures.includes(feature.id) && (
                                    <div className="selected-badge">
                                        <Check size={16} />
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </div>

                    <div className="exterior-preview">
                        <h3>Selected Features</h3>
                        {selectedFeatures.length > 0 ? (
                            <div className="selected-list">
                                {selectedFeatures.map(fId => (
                                    <span key={fId} className="selected-tag">
                                        {EXTERIOR_FEATURES.find(f => f.id === fId)?.name}
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <p className="no-selection">No features selected</p>
                        )}
                    </div>
                </motion.div>

                <div className="exterior-actions">
                    <button className="btn-complete" onClick={markComplete}>
                        <Check size={18} /> Complete Project
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ExteriorModule;
