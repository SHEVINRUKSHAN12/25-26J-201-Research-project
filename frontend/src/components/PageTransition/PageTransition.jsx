import React from 'react';
import { motion } from 'framer-motion';
import './PageTransition.css';

// Smooth fade + subtle slide transition
const pageVariants = {
    initial: {
        opacity: 0,
        y: 8
    },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.35,
            ease: [0.25, 0.46, 0.45, 0.94] // Custom easing for smooth feel
        }
    },
    exit: {
        opacity: 0,
        y: -8,
        transition: {
            duration: 0.25,
            ease: [0.55, 0.06, 0.68, 0.19]
        }
    }
};

const PageTransition = ({ children }) => {
    return (
        <motion.div
            className="page-transition"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
        >
            {children}
        </motion.div>
    );
};

export default PageTransition;
