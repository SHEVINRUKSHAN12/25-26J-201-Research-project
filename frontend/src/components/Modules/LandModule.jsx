import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { db } from '../../firebase';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { ArrowLeft, Upload, Save, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import './LandModule.css';

const LandModule = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [project, setProject] = useState(null);

    const [landData, setLandData] = useState({
        setbackFront: '',
        setbackBack: '',
        setbackLeft: '',
        setbackRight: '',
        far: '',
        maxHeight: '',
        surveyFile: null // Just a placeholder for now
    });

    useEffect(() => {
        const fetchProject = async () => {
            if (!currentUser) return;
            try {
                const docRef = doc(db, 'projects', id);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    const data = docSnap.data();
                    setProject({ id: docSnap.id, ...data });
                    if (data.landData) {
                        setLandData(prev => ({ ...prev, ...data.landData }));
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

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setLandData(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const docRef = doc(db, 'projects', id);
            await updateDoc(docRef, {
                landData: landData,
                landStatus: 'completed' // Mark as completed when saved
            });
            navigate(`/project/${id}`);
        } catch (error) {
            console.error("Error saving land data:", error);
            alert("Failed to save data.");
        }
        setSaving(false);
    };

    if (loading) return <div className="loading-screen">Loading Module...</div>;

    return (
        <div className="module-container">
            <header className="module-header">
                <button onClick={() => navigate(`/project/${id}`)} className="back-btn">
                    <ArrowLeft size={20} /> Back to Project
                </button>
                <div className="header-content">
                    <h1>Land & Rules</h1>
                    <p>Define the constraints and upload survey plans.</p>
                </div>
            </header>

            <div className="module-grid">
                {/* Survey Plan Section */}
                <motion.div
                    className="module-card survey-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h2>Survey Plan</h2>
                    <p>Upload your official survey plan or sketch.</p>

                    <div className="upload-zone">
                        <Upload size={48} />
                        <h3>Drop your file here</h3>
                        <p>Supports PDF, JPG, PNG (Max 10MB)</p>
                        <button className="btn-secondary">Browse Files</button>
                    </div>

                    <div className="file-list">
                        {/* Placeholder for uploaded file */}
                        {landData.surveyFile && (
                            <div className="file-item">
                                <FileText size={20} />
                                <span>survey_plan_v1.pdf</span>
                                <CheckCircle size={16} className="text-green" />
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Rules & Regulations Section */}
                <motion.div
                    className="module-card rules-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <h2>Rules & Regulations</h2>
                    <p>Enter the local building authority regulations.</p>

                    <div className="form-grid">
                        <div className="form-group">
                            <label>Front Setback ({project?.unit})</label>
                            <input
                                type="number"
                                name="setbackFront"
                                value={landData.setbackFront}
                                onChange={handleInputChange}
                                placeholder="e.g. 10"
                            />
                        </div>
                        <div className="form-group">
                            <label>Back Setback ({project?.unit})</label>
                            <input
                                type="number"
                                name="setbackBack"
                                value={landData.setbackBack}
                                onChange={handleInputChange}
                                placeholder="e.g. 5"
                            />
                        </div>
                        <div className="form-group">
                            <label>Left Setback ({project?.unit})</label>
                            <input
                                type="number"
                                name="setbackLeft"
                                value={landData.setbackLeft}
                                onChange={handleInputChange}
                                placeholder="e.g. 3"
                            />
                        </div>
                        <div className="form-group">
                            <label>Right Setback ({project?.unit})</label>
                            <input
                                type="number"
                                name="setbackRight"
                                value={landData.setbackRight}
                                onChange={handleInputChange}
                                placeholder="e.g. 3"
                            />
                        </div>
                        <div className="form-group">
                            <label>Floor Area Ratio (FAR)</label>
                            <input
                                type="number"
                                name="far"
                                value={landData.far}
                                onChange={handleInputChange}
                                placeholder="e.g. 1.5"
                            />
                        </div>
                        <div className="form-group">
                            <label>Max Height ({project?.unit})</label>
                            <input
                                type="number"
                                name="maxHeight"
                                value={landData.maxHeight}
                                onChange={handleInputChange}
                                placeholder="e.g. 35"
                            />
                        </div>
                    </div>
                </motion.div>
            </div>

            <div className="module-actions">
                <button
                    className="btn-primary save-btn"
                    onClick={handleSave}
                    disabled={saving}
                >
                    {saving ? 'Saving...' : 'Save & Continue'} <Save size={18} />
                </button>
            </div>
        </div>
    );
};

export default LandModule;
