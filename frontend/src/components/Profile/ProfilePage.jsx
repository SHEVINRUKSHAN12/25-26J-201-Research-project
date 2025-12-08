import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Calendar, Shield } from 'lucide-react';
import './ProfilePage.css';

const ProfilePage = () => {
    const { currentUser } = useAuth();

    const formatDate = (timestamp) => {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    return (
        <div className="profile-container">
            <div className="profile-header">
                <h1>My Profile</h1>
                <p>Manage your account settings and preferences</p>
            </div>

            <div className="profile-card">
                <div className="profile-avatar">
                    {currentUser?.photoURL ? (
                        <img src={currentUser.photoURL} alt="Profile" />
                    ) : (
                        <div className="avatar-placeholder">
                            <User size={48} />
                        </div>
                    )}
                </div>

                <div className="profile-details">
                    <div className="detail-item">
                        <div className="detail-icon">
                            <User size={20} />
                        </div>
                        <div className="detail-content">
                            <label>Display Name</label>
                            <span>{currentUser?.displayName || 'Not set'}</span>
                        </div>
                    </div>

                    <div className="detail-item">
                        <div className="detail-icon">
                            <Mail size={20} />
                        </div>
                        <div className="detail-content">
                            <label>Email Address</label>
                            <span>{currentUser?.email || 'Not set'}</span>
                        </div>
                    </div>

                    <div className="detail-item">
                        <div className="detail-icon">
                            <Calendar size={20} />
                        </div>
                        <div className="detail-content">
                            <label>Account Created</label>
                            <span>{formatDate(currentUser?.metadata?.creationTime)}</span>
                        </div>
                    </div>

                    <div className="detail-item">
                        <div className="detail-icon">
                            <Shield size={20} />
                        </div>
                        <div className="detail-content">
                            <label>Email Verified</label>
                            <span className={currentUser?.emailVerified ? 'verified' : 'not-verified'}>
                                {currentUser?.emailVerified ? 'Yes' : 'No'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="profile-uid">
                <span className="uid-label">User ID:</span>
                <code>{currentUser?.uid}</code>
            </div>
        </div>
    );
};

export default ProfilePage;
