import React, { useState, useEffect, useRef } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Sun, Moon, User, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './SharedLayout.css';

const SharedLayout = () => {
    // Initialize theme from localStorage or default to 'dark'
    const [theme, setTheme] = useState(() => {
        const savedTheme = localStorage.getItem('theme');
        return savedTheme || 'dark';
    });
    const [isAnimating, setIsAnimating] = useState(false);
    const themeToggleRef = useRef(null);
    const location = useLocation();
    const navigate = useNavigate();
    const { currentUser, logout } = useAuth();

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        if (isAnimating) return;

        const button = themeToggleRef.current;
        const newTheme = theme === 'light' ? 'dark' : 'light';

        // Check if View Transitions API is supported
        if (document.startViewTransition) {
            setIsAnimating(true);

            // Get button position for animation origin
            const rect = button.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;

            // Set CSS variables for animation origin
            document.documentElement.style.setProperty('--theme-x', `${x}px`);
            document.documentElement.style.setProperty('--theme-y', `${y}px`);

            // Use View Transitions API for smooth theme change with content
            const transition = document.startViewTransition(() => {
                setTheme(newTheme);
            });

            transition.finished.then(() => {
                setIsAnimating(false);
            });
        } else {
            // Fallback: Simple theme change for older browsers
            setTheme(newTheme);
        }
    };

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/login');
        } catch (error) {
            console.error("Failed to log out", error);
        }
    };

    return (
        <div className="layout-container">
            <header className="layout-header">
                <Link to="/" className="logo-text">
                    <span className="brand-primary">Home</span> Scope
                </Link>

                <nav className="header-nav">
                    <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Home</Link>
                    <Link to="/about" className={location.pathname === '/about' ? 'active' : ''}>About</Link>
                    <Link to="/contact" className={location.pathname === '/contact' ? 'active' : ''}>Contact</Link>
                    {currentUser && (
                        <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>Dashboard</Link>
                    )}
                </nav>

                <div className="header-actions">
                    <button
                        ref={themeToggleRef}
                        className={`theme-toggle ${isAnimating ? 'animating' : ''}`}
                        onClick={toggleTheme}
                        aria-label="Toggle theme"
                    >
                        {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
                    </button>

                    {currentUser ? (
                        <div className="user-actions">
                            <Link to="/profile" className="user-name">
                                <User size={16} /> {currentUser.displayName?.split(' ')[0]}
                            </Link>
                            <button onClick={handleLogout} className="btn-secondary btn-sm">
                                <LogOut size={16} />
                            </button>
                        </div>
                    ) : (
                        <Link to="/login" className="btn-primary">Get Started</Link>
                    )}
                </div>
            </header>

            <main className="layout-content">
                <Outlet />
            </main>

            <footer className="layout-footer">
                <div className="footer-content">
                    <div className="footer-brand">
                        <span>Home</span> Scope
                    </div>
                    <div className="footer-links">
                        <Link to="/about">About</Link>
                        <Link to="/contact">Contact</Link>
                    </div>
                </div>
                <div className="footer-copyright">
                    © 2025 Home Scope. All rights reserved.
                </div>
            </footer>
        </div>
    );
};

export default SharedLayout;
