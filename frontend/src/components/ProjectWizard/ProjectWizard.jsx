import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, Check, Upload, Ruler, Home, Settings, Map, Compass, Trees, Layers } from 'lucide-react';
import { db } from '../../firebase';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { useAuth } from '../../context/AuthContext';
import './ProjectWizard.css';
import Confetti from '../Confetti/Confetti';

const ProjectWizard = () => {
    const navigate = useNavigate();
    const { currentUser } = useAuth();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        type: 'residential',
        length: '',
        width: '',
        unit: 'ft',
        vastu: true,
        // Modular workflow fields
        mode: 'full', // 'full' or 'individual'
        enabledModules: ['land', 'vastu', 'interior', 'exterior'],
        currentStep: 'land',
        landStatus: 'active',
        vastuStatus: 'pending',
        interiorStatus: 'pending',
        exteriorStatus: 'locked'
    });

    const totalSteps = 4;

    const handleNext = () => setStep(step + 1);
    const handleBack = () => setStep(step - 1);

    const updateData = (field, value) => {
        setFormData({ ...formData, [field]: value });
    };

    const toggleModule = (module) => {
        const current = formData.enabledModules;
        if (current.includes(module)) {
            if (current.length > 1) { // Must have at least one
                updateData('enabledModules', current.filter(m => m !== module));
            }
        } else {
            updateData('enabledModules', [...current, module]);
        }
    };

    const selectMode = (mode) => {
        if (mode === 'full') {
            setFormData({
                ...formData,
                mode: 'full',
                enabledModules: ['land', 'vastu', 'interior', 'exterior'],
                currentStep: 'land',
                landStatus: 'active',
                vastuStatus: 'pending',
                interiorStatus: 'pending',
                exteriorStatus: 'locked'
            });
        } else {
            setFormData({
                ...formData,
                mode: 'individual',
                enabledModules: ['interior'], // Default to interior
                currentStep: 'interior',
                landStatus: 'skipped',
                vastuStatus: 'skipped',
                interiorStatus: 'active',
                exteriorStatus: 'skipped'
            });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        // Update statuses based on enabled modules for individual mode
        let finalData = { ...formData };
        if (formData.mode === 'individual') {
            finalData.landStatus = formData.enabledModules.includes('land') ? 'active' : 'skipped';
            finalData.vastuStatus = formData.enabledModules.includes('vastu') ? 'active' : 'skipped';
            finalData.interiorStatus = formData.enabledModules.includes('interior') ? 'active' : 'skipped';
            finalData.exteriorStatus = formData.enabledModules.includes('exterior') ? 'active' : 'skipped';

            // Set currentStep to first enabled module
            const order = ['land', 'vastu', 'interior', 'exterior'];
            finalData.currentStep = order.find(m => formData.enabledModules.includes(m)) || 'interior';
        }

        try {
            if (!currentUser) {
                alert("Please login to create a project.");
                navigate('/login');
                return;
            }

            // Celebration!
            setShowConfetti(true);
            await new Promise(resolve => setTimeout(resolve, 2000));

            const docRef = await addDoc(collection(db, 'projects'), {
                ...finalData,
                userId: currentUser.uid,
                createdAt: serverTimestamp(),
                status: 'draft'
            });
            navigate(`/project/${docRef.id}`);
        } catch (error) {
            console.error("Error creating project: ", error.message, error);
            alert(`Failed to create project: ${error.message}`);
        }
        setLoading(false);
    };

    const modules = [
        { id: 'land', icon: <Map size={24} />, name: 'Land & Rules', desc: 'Survey plans & regulations' },
        { id: 'vastu', icon: <Compass size={24} />, name: 'Vastu Check', desc: 'Directional compliance' },
        { id: 'interior', icon: <Home size={24} />, name: 'Interior Design', desc: 'Layout optimization' },
        { id: 'exterior', icon: <Trees size={24} />, name: 'Exterior', desc: 'Landscape planning' }
    ];

    return (
        <div className="wizard-container">
            {showConfetti && <Confetti />}
            <div className="wizard-progress">
                {/* Progress Track Background */}
                <div className="progress-track-bg"></div>

                {/* Animated Progress Character */}
                <motion.div
                    className="progress-character"
                    animate={{ left: `${((step - 1) / (totalSteps - 1)) * 100}%` }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                >
                    <div className="character-icon">👷</div>
                    <div className="character-tooltip">Step {step}</div>
                </motion.div>

                <div className={`progress-step ${step >= 1 ? 'active' : ''}`} onClick={() => step > 1 && setStep(1)}>
                    <div className="step-icon"><Layers size={20} /></div>
                    <span>Mode</span>
                </div>
                {/* Removed progress-line divs as they are replaced by track-bg */}
                <div className={`progress-step ${step >= 2 ? 'active' : ''}`} onClick={() => step > 2 && setStep(2)}>
                    <div className="step-icon"><Home size={20} /></div>
                    <span>Basics</span>
                </div>
                <div className={`progress-step ${step >= 3 ? 'active' : ''}`} onClick={() => step > 3 && setStep(3)}>
                    <div className="step-icon"><Ruler size={20} /></div>
                    <span>Dimensions</span>
                </div>
                <div className={`progress-step ${step >= 4 ? 'active' : ''}`} onClick={() => step > 4 && setStep(4)}>
                    <div className="step-icon"><Settings size={20} /></div>
                    <span>Preferences</span>
                </div>
            </div>

            <motion.div
                className="wizard-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <form onSubmit={handleSubmit}>
                    <AnimatePresence mode='wait'>
                        {/* Step 1: Mode Selection */}
                        {step === 1 && (
                            <motion.div
                                key="step1"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="wizard-step"
                            >
                                <h2>Choose Your Path</h2>
                                <p>Select how you want to approach your project.</p>

                                <div className="mode-selection">
                                    <div
                                        className={`mode-card ${formData.mode === 'full' ? 'selected' : ''}`}
                                        onClick={() => selectMode('full')}
                                    >
                                        <div className="mode-icon">🏗️</div>
                                        <h3>Full Suite</h3>
                                        <p>Complete workflow with all modules</p>
                                        <div className="mode-flow">
                                            Land → Vastu → Interior → Exterior
                                        </div>
                                        <span className="mode-badge">Recommended</span>
                                    </div>

                                    <div
                                        className={`mode-card ${formData.mode === 'individual' ? 'selected' : ''}`}
                                        onClick={() => selectMode('individual')}
                                    >
                                        <div className="mode-icon">🎯</div>
                                        <h3>Quick Start</h3>
                                        <p>Pick specific modules to work on</p>

                                        {formData.mode === 'individual' && (
                                            <div className="module-picker">
                                                {modules.map(mod => (
                                                    <div
                                                        key={mod.id}
                                                        className={`module-chip ${formData.enabledModules.includes(mod.id) ? 'active' : ''}`}
                                                        onClick={(e) => { e.stopPropagation(); toggleModule(mod.id); }}
                                                    >
                                                        {mod.icon}
                                                        <span>{mod.name}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* Step 2: Project Basics */}
                        {step === 2 && (
                            <motion.div
                                key="step2"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="wizard-step"
                            >
                                <h2>Project Basics</h2>
                                <p>Let's start with the fundamental details of your project.</p>

                                <div className="form-group">
                                    <label>Project Name</label>
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => updateData('name', e.target.value)}
                                        placeholder="e.g., Dream Villa 2025"
                                        autoFocus
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Project Type</label>
                                    <div className="type-grid">
                                        <div
                                            className={`type-card ${formData.type === 'residential' ? 'selected' : ''}`}
                                            onClick={() => updateData('type', 'residential')}
                                        >
                                            <h3>Residential</h3>
                                            <p>Homes, Apartments, Villas</p>
                                        </div>
                                        <div
                                            className={`type-card ${formData.type === 'commercial' ? 'selected' : ''}`}
                                            onClick={() => updateData('type', 'commercial')}
                                        >
                                            <h3>Commercial</h3>
                                            <p>Offices, Shops, Restaurants</p>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* Step 3: Dimensions */}
                        {step === 3 && (
                            <motion.div
                                key="step3"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="wizard-step"
                            >
                                <h2>Dimensions</h2>
                                <p>Enter the plot size or upload a blueprint.</p>

                                <div className="dimensions-grid">
                                    <div className="form-group">
                                        <label>Length</label>
                                        <input
                                            type="number"
                                            value={formData.length}
                                            onChange={(e) => updateData('length', e.target.value)}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Width</label>
                                        <input
                                            type="number"
                                            value={formData.width}
                                            onChange={(e) => updateData('width', e.target.value)}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Unit</label>
                                        <select
                                            value={formData.unit}
                                            onChange={(e) => updateData('unit', e.target.value)}
                                        >
                                            <option value="ft">Feet</option>
                                            <option value="m">Meters</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="divider">OR</div>

                                <div className="upload-box">
                                    <Upload size={32} />
                                    <p>Upload Blueprint / Sketch</p>
                                    <span>Supports JPG, PNG, PDF</span>
                                </div>
                            </motion.div>
                        )}

                        {/* Step 4: Preferences */}
                        {step === 4 && (
                            <motion.div
                                key="step4"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="wizard-step"
                            >
                                <h2>Preferences</h2>
                                <p>Customize the optimization parameters.</p>

                                <div className="form-group">
                                    <label className="checkbox-label">
                                        <input
                                            type="checkbox"
                                            checked={formData.vastu}
                                            onChange={(e) => updateData('vastu', e.target.checked)}
                                        />
                                        <span className="checkbox-custom"></span>
                                        Enable Vastu Compliance
                                    </label>
                                </div>

                                <div className="summary-box">
                                    <h4>Project Summary</h4>
                                    <div className="summary-item">
                                        <span>Mode:</span>
                                        <strong>{formData.mode === 'full' ? 'Full Suite' : 'Quick Start'}</strong>
                                    </div>
                                    <div className="summary-item">
                                        <span>Modules:</span>
                                        <strong>{formData.enabledModules.map(m => m.charAt(0).toUpperCase() + m.slice(1)).join(', ')}</strong>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="wizard-actions">
                        {step > 1 && (
                            <button type="button" className="btn-secondary" onClick={handleBack}>
                                <ArrowLeft size={18} /> Back
                            </button>
                        )}

                        {step < totalSteps ? (
                            <button type="button" className="btn-primary" onClick={handleNext}>
                                Next <ArrowRight size={18} />
                            </button>
                        ) : (
                            <button disabled={loading} type="submit" className="btn-primary">
                                {loading ? 'Creating...' : 'Create Project'} <Check size={18} />
                            </button>
                        )}
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default ProjectWizard;
