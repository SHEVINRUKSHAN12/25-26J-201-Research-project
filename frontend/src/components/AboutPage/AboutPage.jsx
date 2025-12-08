import React from 'react';
import { motion } from 'framer-motion';
import './AboutPage.css';

const AboutPage = () => {
    return (
        <div className="about-page">
            <section className="about-hero">
                <motion.div
                    className="about-hero-content"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <h1>About <span className="text-gradient">Home Scope</span></h1>
                    <p className="subtitle">Revolutionizing interior and exterior space optimization with intelligent design.</p>
                </motion.div>
            </section>

            <section className="about-mission">
                <div className="container">
                    <motion.div
                        className="mission-content"
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                    >
                        <h2>Our Mission</h2>
                        <p>
                            At Home Scope, we believe that every space has the potential to be both beautiful and functional.
                            Our mission is to empower homeowners and builders with advanced tools that simplify the complex process of
                            space planning. By integrating land analysis, Vastu principles, and modern design aesthetics,
                            we provide a holistic approach to creating your dream home.
                        </p>
                    </motion.div>
                </div>
            </section>

            <section className="key-findings">
                <div className="container">
                    <motion.div
                        className="findings-header"
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        <h2>Key Findings</h2>
                    </motion.div>
                    <div className="findings-grid">
                        <motion.div
                            className="finding-card"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.1 }}
                        >
                            <h3>Automated Compliance</h3>
                            <p>Our system reduces the time required for regulatory checks by 90%, ensuring instant feedback on setbacks and coverage.</p>
                        </motion.div>
                        <motion.div
                            className="finding-card"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                        >
                            <h3>Vastu Integration</h3>
                            <p>We've successfully quantified Vastu principles into algorithmic constraints, allowing for seamless integration with modern design.</p>
                        </motion.div>
                        <motion.div
                            className="finding-card"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.3 }}
                        >
                            <h3>Space Efficiency</h3>
                            <p>Optimized layouts demonstrate a 15-20% increase in usable floor area compared to conventional manual planning methods.</p>
                        </motion.div>
                    </div>
                </div>
            </section>

            <section className="about-team">
                <div className="container">
                    <motion.div
                        className="team-header"
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        <h2>The Project</h2>
                        <p>
                            Home Scope is a research-driven initiative aimed at solving real-world challenges in residential construction.
                            We combine architectural expertise with cutting-edge technology to deliver optimized layouts that respect
                            traditional values while embracing modern living standards.
                        </p>
                    </motion.div>
                </div>
            </section>
        </div>
    );
};

export default AboutPage;
