import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { db } from '../../firebase';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { ArrowLeft, Map, Compass, Home, Trees, CheckCircle, Lock, SkipForward, Play, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import './ProjectDetails.css';

const ProjectDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProject = async () => {
            if (!currentUser) return;
            try {
                const docRef = doc(db, 'projects', id);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    setProject({ id: docSnap.id, ...docSnap.data() });
                } else {
                    console.log("No such project!");
                    navigate('/dashboard');
                }
            } catch (error) {
                console.error("Error fetching project:", error);
            }
            setLoading(false);
        };

        fetchProject();
    }, [id, currentUser, navigate]);

    const updateModuleStatus = async (moduleId, newStatus) => {
        if (!project) return;

        const statusField = `${moduleId}Status`;
        const updates = { [statusField]: newStatus };

        // If completing a module, activate the next one
        if (newStatus === 'completed') {
            const order = ['land', 'vastu', 'interior', 'exterior'];
            const currentIndex = order.indexOf(moduleId);
            if (currentIndex < order.length - 1) {
                const nextModule = order[currentIndex + 1];
                const nextStatusField = `${nextModule}Status`;
                if (project[nextStatusField] === 'pending' || project[nextStatusField] === 'locked') {
                    updates[nextStatusField] = 'active';
                    updates.currentStep = nextModule;
                }
            }
        }

        // If skipping a module, activate the next one
        if (newStatus === 'skipped') {
            const order = ['land', 'vastu', 'interior', 'exterior'];
            const currentIndex = order.indexOf(moduleId);
            if (currentIndex < order.length - 1) {
                const nextModule = order[currentIndex + 1];
                const nextStatusField = `${nextModule}Status`;
                if (project[nextStatusField] === 'pending' || project[nextStatusField] === 'locked') {
                    updates[nextStatusField] = 'active';
                    updates.currentStep = nextModule;
                }
            }
        }

        try {
            await updateDoc(doc(db, 'projects', id), updates);
            setProject({ ...project, ...updates });
        } catch (error) {
            console.error("Error updating module status:", error);
        }
    };

    const handleModuleClick = (module) => {
        if (module.status === 'locked') return;
        navigate(`/project/${id}/${module.id}`);
    };

    if (loading) return <div className="loading-screen">Loading Project...</div>;
    if (!project) return null;

    const modules = [
        {
            id: 'land',
            title: 'Land & Rules',
            icon: <Map size={24} />,
            description: 'Upload survey plans, define setbacks, and check regulations.',
            status: project.landStatus || 'pending',
            color: '#3b82f6'
        },
        {
            id: 'vastu',
            title: 'Vastu Check',
            icon: <Compass size={24} />,
            description: 'Analyze directional compliance and energy flow.',
            status: project.vastuStatus || 'pending',
            color: '#f59e0b'
        },
        {
            id: 'interior',
            title: 'Interior Design',
            icon: <Home size={24} />,
            description: 'Optimize layout, furniture placement, and aesthetics.',
            status: project.interiorStatus || 'pending',
            color: '#8b5cf6'
        },
        {
            id: 'exterior',
            title: 'Exterior & Landscape',
            icon: <Trees size={24} />,
            description: 'Plan gardens, parking, and outdoor living spaces.',
            status: project.exteriorStatus || 'locked',
            color: '#10b981'
        }
    ];

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed': return <CheckCircle size={16} />;
            case 'locked': return <Lock size={16} />;
            case 'skipped': return <SkipForward size={16} />;
            case 'active': return <Play size={16} />;
            default: return null;
        }
    };

    const getStatusLabel = (status) => {
        switch (status) {
            case 'completed': return 'Completed';
            case 'locked': return 'Locked';
            case 'skipped': return 'Skipped';
            case 'active': return 'In Progress';
            case 'pending': return 'Pending';
            default: return status;
        }
    };

    return (
        <div className="project-hub-container">
            <header className="hub-header">
                <button onClick={() => navigate('/dashboard')} className="back-btn">
                    <ArrowLeft size={18} /> Back to Dashboard
                </button>
                <div className="project-title">
                    <h1>{project.name}</h1>
                    <span className={`project-mode ${project.mode}`}>
                        {project.mode === 'full' ? 'Full Suite' : 'Quick Start'}
                    </span>
                </div>
            </header>

            {/* Progress Stepper */}
            <div className="progress-stepper">
                {modules.map((module, index) => (
                    <React.Fragment key={module.id}>
                        <motion.div
                            className={`stepper-step ${module.status}`}
                            whileHover={{ scale: module.status !== 'locked' ? 1.05 : 1 }}
                            onClick={() => module.status !== 'locked' && handleModuleClick(module)}
                        >
                            <div
                                className="stepper-icon"
                                style={{
                                    borderColor: module.status === 'completed' || module.status === 'active' ? module.color : undefined,
                                    background: module.status === 'completed' ? module.color : undefined
                                }}
                            >
                                {module.status === 'completed' ? <CheckCircle size={20} /> : module.icon}
                            </div>
                            <span className="stepper-label">{module.title}</span>
                            <span className="stepper-status">{getStatusLabel(module.status)}</span>
                        </motion.div>
                        {index < modules.length - 1 && (
                            <div className={`stepper-line ${modules[index + 1].status === 'completed' || modules[index + 1].status === 'active' ? 'active' : ''}`}></div>
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* Module Cards */}
            <div className="modules-grid">
                {modules.map((module, index) => (
                    <motion.div
                        key={module.id}
                        className={`module-card ${module.status}`}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        style={{ '--module-color': module.color }}
                    >
                        <div className="module-header">
                            <div className="module-icon" style={{ color: module.color }}>
                                {module.icon}
                            </div>
                            <span className={`status-badge ${module.status}`}>
                                {getStatusIcon(module.status)}
                                {getStatusLabel(module.status)}
                            </span>
                        </div>

                        <h3>{module.title}</h3>
                        <p>{module.description}</p>

                        <div className="module-actions">
                            {module.status === 'active' && (
                                <>
                                    <button
                                        className="btn-primary"
                                        onClick={() => handleModuleClick(module)}
                                    >
                                        Open <ChevronRight size={16} />
                                    </button>
                                    <button
                                        className="btn-secondary"
                                        onClick={() => updateModuleStatus(module.id, 'skipped')}
                                    >
                                        Skip
                                    </button>
                                </>
                            )}
                            {module.status === 'pending' && (
                                <button
                                    className="btn-outline"
                                    disabled
                                >
                                    Complete previous step
                                </button>
                            )}
                            {module.status === 'completed' && (
                                <button
                                    className="btn-outline"
                                    onClick={() => handleModuleClick(module)}
                                >
                                    Review
                                </button>
                            )}
                            {module.status === 'skipped' && (
                                <button
                                    className="btn-outline"
                                    onClick={() => updateModuleStatus(module.id, 'active')}
                                >
                                    Start Now
                                </button>
                            )}
                            {module.status === 'locked' && (
                                <button className="btn-locked" disabled>
                                    <Lock size={14} /> Locked
                                </button>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
                <h4>Project Info</h4>
                <div className="info-grid">
                    <div className="info-item">
                        <span>Type</span>
                        <strong>{project.type === 'residential' ? 'Residential' : 'Commercial'}</strong>
                    </div>
                    <div className="info-item">
                        <span>Dimensions</span>
                        <strong>{project.length} × {project.width} {project.unit}</strong>
                    </div>
                    <div className="info-item">
                        <span>Vastu</span>
                        <strong>{project.vastu ? 'Enabled' : 'Disabled'}</strong>
                    </div>
                    <div className="info-item">
                        <span>Budget</span>
                        <strong>{project.budget?.charAt(0).toUpperCase() + project.budget?.slice(1)}</strong>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProjectDetails;
