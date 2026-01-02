import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User, AlertCircle, Eye, EyeOff, CheckCircle } from 'lucide-react';
import './Auth.css';

const SignupPage = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { signup, googleLogin } = useAuth();
    const navigate = useNavigate();

    // Password strength checker
    const getPasswordStrength = () => {
        if (!password) return { strength: 0, text: '', color: '' };
        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        const levels = [
            { text: 'Weak', color: '#ef4444' },
            { text: 'Fair', color: '#f59e0b' },
            { text: 'Good', color: '#3b82f6' },
            { text: 'Strong', color: '#22c55e' }
        ];
        return { strength, ...levels[strength - 1] || { text: '', color: '' } };
    };

    const passwordStrength = getPasswordStrength();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            return setError('Passwords do not match');
        }

        if (password.length < 6) {
            return setError('Password must be at least 6 characters');
        }

        try {
            setError('');
            setLoading(true);
            await signup(email, password, name);
            navigate('/dashboard');
        } catch (err) {
            setError('Failed to create an account. ' + err.message);
            console.error(err);
        }
        setLoading(false);
    };

    const handleGoogleLogin = async () => {
        try {
            setError('');
            await googleLogin();
            navigate('/dashboard');
        } catch (err) {
            setError('Failed to sign up with Google.');
            console.error(err);
        }
    };

    return (
        <div className="auth-container">
            <motion.div
                className="auth-card"
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
            >
                <div className="auth-header">
                    <motion.h2
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        Create Account
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                    >
                        Join Home Scope and start designing
                    </motion.p>
                </div>

                {error && (
                    <motion.div
                        className="auth-error"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <AlertCircle size={18} />
                        <span>{error}</span>
                    </motion.div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    <motion.div
                        className="form-group"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.25 }}
                    >
                        <label htmlFor="name">Full Name</label>
                        <div className="input-wrapper">
                            <User size={18} className="input-icon" />
                            <input
                                id="name"
                                type="text"
                                required
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="John Doe"
                                autoComplete="name"
                            />
                        </div>
                    </motion.div>

                    <motion.div
                        className="form-group"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <label htmlFor="email">Email Address</label>
                        <div className="input-wrapper">
                            <Mail size={18} className="input-icon" />
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="name@example.com"
                                autoComplete="email"
                            />
                        </div>
                    </motion.div>

                    <motion.div
                        className="form-group"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.35 }}
                    >
                        <label htmlFor="password">Password</label>
                        <div className="input-wrapper">
                            <Lock size={18} className="input-icon" />
                            <input
                                id="password"
                                type={showPassword ? 'text' : 'password'}
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Create a strong password"
                                autoComplete="new-password"
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowPassword(!showPassword)}
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                        {password && (
                            <div className="password-strength">
                                <div className="strength-bar">
                                    <div
                                        className="strength-fill"
                                        style={{
                                            width: `${passwordStrength.strength * 25}%`,
                                            backgroundColor: passwordStrength.color
                                        }}
                                    />
                                </div>
                                <span style={{ color: passwordStrength.color }}>
                                    {passwordStrength.text}
                                </span>
                            </div>
                        )}
                    </motion.div>

                    <motion.div
                        className="form-group"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <div className="input-wrapper">
                            <Lock size={18} className="input-icon" />
                            <input
                                id="confirmPassword"
                                type={showConfirmPassword ? 'text' : 'password'}
                                required
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="Confirm your password"
                                autoComplete="new-password"
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                tabIndex={-1}
                            >
                                {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                        {confirmPassword && password === confirmPassword && (
                            <div className="password-match">
                                <CheckCircle size={14} />
                                <span>Passwords match</span>
                            </div>
                        )}
                    </motion.div>

                    <motion.button
                        disabled={loading}
                        type="submit"
                        className="btn-primary auth-btn"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.45 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        {loading ? (
                            <>
                                <span className="loading-spinner"></span>
                                Creating Account...
                            </>
                        ) : (
                            <>
                                Create Account <UserPlus size={18} />
                            </>
                        )}
                    </motion.button>
                </form>

                <div className="auth-divider">
                    <span>or continue with</span>
                </div>

                <motion.button
                    type="button"
                    onClick={handleGoogleLogin}
                    className="auth-btn google-btn"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" />
                    Continue with Google
                </motion.button>

                <motion.div
                    className="auth-footer"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.55 }}
                >
                    Already have an account? <Link to="/login">Sign In</Link>
                </motion.div>
            </motion.div>
        </div>
    );
};

export default SignupPage;
