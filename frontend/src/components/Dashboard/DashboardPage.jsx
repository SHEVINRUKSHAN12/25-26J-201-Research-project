import { motion, useMotionValue, useTransform, animate } from 'framer-motion';

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Plus, Layout, Clock, ArrowRight, Folder, Compass, Map, Home, Trees, Trash2, Check, X } from 'lucide-react';
import { db } from '../../firebase';
import { collection, query, where, getDocs, doc, deleteDoc, updateDoc } from 'firebase/firestore';
import './Dashboard.css';
import ConfirmModal from '../common/ConfirmModal';
import { ToastContainer, useToast } from '../common/Toast';

const StatCard = ({ icon, value, label, colorClass, delay }) => {
    const count = useMotionValue(0);
    const rounded = useTransform(count, Math.round);

    useEffect(() => {
        const animation = animate(count, value, { duration: 2, delay: delay });
        return animation.stop;
    }, [value, delay]);

    return (
        <motion.div
            className="bento-card card-stat"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: delay, duration: 0.5 }}
            whileHover={{ y: -5, boxShadow: "0 15px 30px rgba(0,0,0,0.2)" }}
        >
            <div className={`stat-icon ${colorClass}`}>
                {icon}
            </div>
            <div>
                <motion.div className="stat-value">{rounded}</motion.div>
                <div className="stat-label">{label}</div>
            </div>
        </motion.div>
    );
};

const DashboardPage = () => {
    const { currentUser } = useAuth();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [editName, setEditName] = useState('');
    const [deleteModal, setDeleteModal] = useState({ isOpen: false, projectId: null, projectName: '' });
    const { toasts, addToast, removeToast } = useToast();

    useEffect(() => {
        const fetchProjects = async () => {
            if (!currentUser) {
                setLoading(false);
                return;
            }
            try {
                // Simple query without orderBy (works without composite index)
                const q = query(
                    collection(db, 'projects'),
                    where('userId', '==', currentUser.uid)
                );
                const querySnapshot = await getDocs(q);
                const projectsData = querySnapshot.docs.map(doc => ({
                    id: doc.id,
                    ...doc.data()
                }));
                // Sort client-side instead
                projectsData.sort((a, b) => {
                    const dateA = a.createdAt?.toDate?.() || new Date(0);
                    const dateB = b.createdAt?.toDate?.() || new Date(0);
                    return dateB - dateA;
                });
                setProjects(projectsData);
                setError(null);
            } catch (err) {
                console.error("Error fetching projects:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, [currentUser]);

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good Morning';
        if (hour < 18) return 'Good Afternoon';
        return 'Good Evening';
    };

    const openDeleteModal = (e, project) => {
        e.preventDefault();
        e.stopPropagation();
        setDeleteModal({ isOpen: true, projectId: project.id, projectName: project.name || 'Untitled Project' });
    };

    const closeDeleteModal = () => {
        setDeleteModal({ isOpen: false, projectId: null, projectName: '' });
    };

    const confirmDelete = async () => {
        const projectName = deleteModal.projectName;
        try {
            await deleteDoc(doc(db, 'projects', deleteModal.projectId));
            setProjects(prev => prev.filter(p => p.id !== deleteModal.projectId));
            closeDeleteModal();
            addToast(`"${projectName}" deleted successfully`, 'success');
        } catch (err) {
            console.error('Error deleting project:', err);
            addToast('Failed to delete project: ' + err.message, 'error');
            closeDeleteModal();
        }
    };

    const cancelEditing = (e) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        setEditingId(null);
        setEditName('');
    };

    const saveEdit = async (e, projectId) => {
        e.preventDefault();
        e.stopPropagation();
        if (!editName.trim()) return;
        try {
            await updateDoc(doc(db, 'projects', projectId), { name: editName.trim() });
            setProjects(prev => prev.map(p =>
                p.id === projectId ? { ...p, name: editName.trim() } : p
            ));
            setEditingId(null);
            setEditName('');
        } catch (err) {
            console.error('Error updating project:', err);
            alert('Failed to update project: ' + err.message);
        }
    };

    return (
        <div className="dashboard-container">
            <div className="aurora-bg"></div>

            <header className="dashboard-header">
                <div className="header-content">
                    <h1>{getGreeting()}, {currentUser?.displayName?.split(' ')[0]}</h1>
                    <p>Here's what's happening with your projects today.</p>
                </div>
                <Link to="/new-project" className="new-project-btn">
                    <Plus size={20} /> New Project
                </Link>
            </header>

            <div className="bento-grid">
                {/* Welcome Card */}
                <motion.div
                    className="bento-card card-welcome"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    <div>
                        <h2>Start a New Module</h2>
                        <p>Begin your optimization journey by selecting a specific module or creating a full project suite.</p>
                    </div>
                    <div className="welcome-actions">
                        <Link to="/new-project?module=land" className="action-btn">
                            <Map size={18} /> Land
                        </Link>
                        <Link to="/new-project?module=vastu" className="action-btn">
                            <Compass size={18} /> Vastu
                        </Link>
                        <Link to="/new-project?module=interior" className="action-btn">
                            <Home size={18} /> Interior
                        </Link>
                        <Link to="/new-project?module=exterior" className="action-btn">
                            <Trees size={18} /> Exterior
                        </Link>
                    </div>
                </motion.div>

                {/* Stats Cards */}
                <StatCard
                    icon={<Layout size={24} />}
                    value={projects.length}
                    label="Total Projects"
                    colorClass="bg-blue"
                    delay={0.1}
                />

                <StatCard
                    icon={<Clock size={24} />}
                    value={projects.filter(p => p.status === 'draft').length}
                    label="In Progress"
                    colorClass="bg-purple"
                    delay={0.2}
                />

                <StatCard
                    icon={<Folder size={24} />}
                    value={projects.filter(p => p.status === 'completed').length}
                    label="Completed"
                    colorClass="bg-green"
                    delay={0.3}
                />

                <StatCard
                    icon={<Compass size={24} />}
                    value={0}
                    label="Vastu Checks"
                    colorClass="bg-orange"
                    delay={0.4}
                />
            </div>

            <section className="projects-section">
                <div className="section-header">
                    <h2>Recent Projects</h2>
                    <Link to="/projects" className="view-all">View All <ArrowRight size={16} /></Link>
                </div>

                {loading ? (
                    <div className="loading-state">Loading projects...</div>
                ) : projects.length > 0 ? (
                    <div className="projects-grid">
                        {projects.map(project => (
                            <div key={project.id} className="project-card-wrapper">
                                <Link
                                    to={editingId === project.id ? '#' : `/project/${project.id}`}
                                    className="project-card"
                                    onClick={e => {
                                        if (editingId === project.id) {
                                            e.preventDefault();
                                        }
                                    }}
                                >
                                    <div className="project-preview">
                                        <Layout size={48} strokeWidth={1} />
                                    </div>
                                    <div className="project-info">
                                        {editingId === project.id ? (
                                            <div className="edit-name-form" onClick={e => e.preventDefault()}>
                                                <input
                                                    type="text"
                                                    value={editName}
                                                    onChange={e => setEditName(e.target.value)}
                                                    onClick={e => e.stopPropagation()}
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter') saveEdit(e, project.id);
                                                        if (e.key === 'Escape') cancelEditing(e);
                                                    }}
                                                    placeholder="Enter project name"
                                                    autoFocus
                                                />
                                                <button
                                                    className="edit-btn save"
                                                    onClick={e => saveEdit(e, project.id)}
                                                    disabled={!editName.trim()}
                                                    title="Save"
                                                >
                                                    <Check size={16} />
                                                </button>
                                                <button className="edit-btn cancel" onClick={cancelEditing} title="Cancel">
                                                    <X size={16} />
                                                </button>
                                            </div>
                                        ) : (
                                            <h3
                                                className="editable-name"
                                                onClick={e => {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                    setEditingId(project.id);
                                                    setEditName(project.name);
                                                }}
                                                title="Click to edit name"
                                            >
                                                {project.name || 'Untitled Project'}
                                            </h3>
                                        )}
                                        <div className="project-meta">
                                            <span>{project.type || 'residential'}</span>
                                            <span>•</span>
                                            <span>{project.length || 0}x{project.width || 0} {project.unit || 'ft'}</span>
                                        </div>
                                        <div className="module-tags">
                                            {(project.landStatus === 'active' || project.landStatus === 'completed') && (
                                                <span className={`module-tag ${project.landStatus === 'completed' ? 'completed' : 'active'}`}>Land</span>
                                            )}
                                            {(project.vastuStatus === 'active' || project.vastuStatus === 'completed') && (
                                                <span className={`module-tag ${project.vastuStatus === 'completed' ? 'completed' : 'active'}`}>Vastu</span>
                                            )}
                                            {(project.interiorStatus === 'active' || project.interiorStatus === 'completed') && (
                                                <span className={`module-tag ${project.interiorStatus === 'completed' ? 'completed' : 'active'}`}>Interior</span>
                                            )}
                                            {(project.exteriorStatus === 'active' || project.exteriorStatus === 'completed') && (
                                                <span className={`module-tag ${project.exteriorStatus === 'completed' ? 'completed' : 'active'}`}>Exterior</span>
                                            )}
                                        </div>
                                    </div>
                                </Link>
                                <button
                                    className="action-icon delete"
                                    onClick={e => openDeleteModal(e, project)}
                                    title="Delete project"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <div className="empty-icon">
                            <Layout size={40} />
                        </div>
                        <h3>No projects yet</h3>
                        <p>Start your first interior design project today.</p>
                        <Link to="/new-project" className="new-project-btn" style={{ display: 'inline-flex' }}>
                            Create Project
                        </Link>
                    </div>
                )}
            </section>

            <ConfirmModal
                isOpen={deleteModal.isOpen}
                onClose={closeDeleteModal}
                onConfirm={confirmDelete}
                title="Delete Project"
                message={`Are you sure you want to delete "${deleteModal.projectName}"? This action cannot be undone.`}
                confirmText="Delete"
                cancelText="Cancel"
                type="danger"
            />

            <ToastContainer toasts={toasts} removeToast={removeToast} />
        </div>
    );
};

export default DashboardPage;
