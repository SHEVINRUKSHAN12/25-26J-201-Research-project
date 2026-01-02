import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const Confetti = () => {
    const [particles, setParticles] = useState([]);

    useEffect(() => {
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
        const newParticles = Array.from({ length: 100 }).map((_, i) => ({
            id: i,
            x: Math.random() * 100, // vw
            y: -10, // start above screen
            color: colors[Math.floor(Math.random() * colors.length)],
            size: Math.random() * 8 + 4,
            rotation: Math.random() * 360,
            delay: Math.random() * 0.5
        }));
        setParticles(newParticles);
    }, []);

    return (
        <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 9999, overflow: 'hidden' }}>
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    initial={{ y: '-10vh', x: `${p.x}vw`, rotate: 0, opacity: 1 }}
                    animate={{
                        y: '110vh',
                        x: `${p.x + (Math.random() * 20 - 10)}vw`,
                        rotate: p.rotation + 720,
                        opacity: 0
                    }}
                    transition={{
                        duration: Math.random() * 2 + 2,
                        ease: "linear",
                        delay: p.delay
                    }}
                    style={{
                        position: 'absolute',
                        width: p.size,
                        height: p.size,
                        backgroundColor: p.color,
                        borderRadius: Math.random() > 0.5 ? '50%' : '2px'
                    }}
                />
            ))}
        </div>
    );
};

export default Confetti;
