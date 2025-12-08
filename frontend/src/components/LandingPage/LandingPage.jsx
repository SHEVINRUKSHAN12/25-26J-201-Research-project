import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout, Armchair, Compass, Trees, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence, useMotionValue, useTransform, useMotionTemplate } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import './LandingPage.css';

// ... (existing code)

// 3D Tilt Card Component
const TiltCard = ({ children }) => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateX = useTransform(y, [-100, 100], [5, -5]);
  const rotateY = useTransform(x, [-100, 100], [-5, 5]);

  const handleMouseMove = ({ currentTarget, clientX, clientY }) => {
    const { left, top, width, height } = currentTarget.getBoundingClientRect();
    x.set(clientX - (left + width / 2));
    y.set(clientY - (top + height / 2));
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      className="tilt-card-container"
      style={{
        perspective: 1000,
        rotateX,
        rotateY,
        transformStyle: "preserve-3d"
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        className="spotlight-overlay"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              600px circle at ${mouseX}px ${mouseY}px,
              rgba(255,255,255,0.06),
              transparent 80%
            )
          `,
          position: 'absolute',
          inset: 0,
          borderRadius: '16px',
          zIndex: 10,
          pointerEvents: 'none'
        }}
      />
      {children}
      <motion.div
        className="card-glare"
        style={{
          opacity: useTransform(x, [-100, 0, 100], [0, 0.3, 0]),
          background: 'linear-gradient(105deg, transparent 20%, rgba(255,255,255,0.2) 50%, transparent 80%)',
          position: 'absolute',
          inset: 0,
          borderRadius: '16px',
          zIndex: 11,
          pointerEvents: 'none',
          mixBlendMode: 'overlay'
        }}
      />
    </motion.div>
  );
};
// Hook for mouse position
const useMousePosition = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const updateMousePosition = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", updateMousePosition);
    return () => window.removeEventListener("mousemove", updateMousePosition);
  }, []);

  return mousePosition;
};

// Custom Cursor Component
const CustomCursor = () => {
  const { x, y } = useMousePosition();
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const handleMouseOver = (e) => {
      if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('.feature-card')) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };
    document.addEventListener('mouseover', handleMouseOver);
    return () => document.removeEventListener('mouseover', handleMouseOver);
  }, []);

  return (
    <motion.div
      className="custom-cursor"
      animate={{
        x: x - 16,
        y: y - 16,
        scale: isHovering ? 1.5 : 1,
        opacity: 1
      }}
      transition={{
        type: "spring",
        stiffness: 500,
        damping: 28,
        mass: 0.5
      }}
    >
      <div className="cursor-dot" />
    </motion.div>
  );
};



// Particle Background Component
const ParticleBackground = () => {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 20 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 1,
      duration: Math.random() * 20 + 10
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="particle-background">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="particle"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -100, 0],
            opacity: [0.2, 0.5, 0.2],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      ))}
    </div>
  );
};

const stages = ['blueprint', 'land', 'vastu', 'interior', 'exterior'];

const LandingPage = () => {
  const { currentUser } = useAuth();

  // Animation Sequence State
  const [activeStage, setActiveStage] = useState(0);
  const stageLabels = {
    blueprint: "Blueprint Phase",
    land: "Land Optimization",
    vastu: "Vastu Check",
    interior: "Interior Design",
    exterior: "Exterior Planning"
  };



  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % stages.length);
    }, 3500); // Change stage every 3.5 seconds
    return () => clearInterval(interval);
  }, []);



  const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="landing-container">
      <CustomCursor />
      <ParticleBackground />



      {/* Hero Section */}
      <section className="hero-section">
        <motion.div
          className="hero-content"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          {/* Animated Sketch Above Title */}
          <motion.div
            className="sketch-animation"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <svg viewBox="0 0 200 60" className="sketch-svg">
              {/* House outline sketch */}
              <motion.path
                d="M40 45 L40 25 L60 10 L80 25 L80 45 L40 45"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 2,
                  ease: "easeInOut",
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 3
                }}
              />
              {/* Door */}
              <motion.path
                d="M55 45 L55 32 L65 32 L65 45"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 1,
                  ease: "easeInOut",
                  delay: 1.5,
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 4
                }}
              />
              {/* Window */}
              <motion.rect
                x="45" y="30" width="8" height="8"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 1,
                  ease: "easeInOut",
                  delay: 1.8,
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 4
                }}
              />
              {/* Pencil */}
              <motion.g
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 100, opacity: [0, 1, 1, 0] }}
                transition={{
                  duration: 3,
                  ease: "easeInOut",
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 2
                }}
              >
                <rect x="0" y="25" width="20" height="6" rx="1" fill="var(--accent-primary)" />
                <polygon points="20,25 25,28 20,31" fill="var(--text-secondary)" />
              </motion.g>
              {/* Grid/blueprint lines */}
              <motion.line
                x1="100" y1="20" x2="180" y2="20"
                stroke="currentColor"
                strokeWidth="1"
                strokeDasharray="4 4"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.5 }}
                transition={{
                  duration: 1,
                  delay: 2,
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 4
                }}
              />
              <motion.line
                x1="100" y1="35" x2="160" y2="35"
                stroke="currentColor"
                strokeWidth="1"
                strokeDasharray="4 4"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.5 }}
                transition={{
                  duration: 1,
                  delay: 2.3,
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 4
                }}
              />
              <motion.line
                x1="100" y1="50" x2="140" y2="50"
                stroke="currentColor"
                strokeWidth="1"
                strokeDasharray="4 4"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.5 }}
                transition={{
                  duration: 1,
                  delay: 2.5,
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 4
                }}
              />
            </svg>
          </motion.div>

          <motion.h1 className="hero-title" variants={fadeInUp}>
            Design Smarter.<br />
            <span className="text-gradient">Build Smarter.</span>
          </motion.h1>
          <motion.p className="hero-subtitle" variants={fadeInUp}>
            An intelligent platform that transforms land planning,
            interior design, exterior layout, and Vastu alignment into reality.
          </motion.p>
          <motion.div className="hero-cta-group" variants={fadeInUp}>
            <Link to={currentUser ? "/dashboard" : "/signup"} className="btn-primary btn-lg">
              Start Designing <ArrowRight size={18} />
            </Link>
            <button className="btn-secondary">View Demo</button>
          </motion.div>
        </motion.div>

        <motion.div
          className="hero-image-container"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {/* Dynamic Hero Visual - Magical Sequence */}
          <div className={`hero-visual-wrapper stage-${stages[activeStage]}`}>
            <div className="visual-glow"></div>

            {/* Stage Indicators */}
            <div className="stage-indicators">
              {stages.map((stage, index) => (
                <div
                  key={stage}
                  className={`stage-dot ${index === activeStage ? 'active' : ''}`}
                />
              ))}
            </div>

            {/* Stage Label */}
            <AnimatePresence mode='wait'>
              <motion.div
                key={activeStage}
                className="stage-label"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                {stageLabels[stages[activeStage]]}
              </motion.div>
            </AnimatePresence>

            {/* Central House Core (Always Visible) */}
            <div className="house-core">
              <div className="house-roof"></div>
              <div className="house-body">
                <div className="door-frame"></div>
                <div className="window-glow"></div>
              </div>
            </div>

            {/* Stage 1: Blueprint Grid */}
            <AnimatePresence>
              {(stages[activeStage] === 'blueprint' || stages[activeStage] === 'land') && (
                <motion.div
                  className="blueprint-grid"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="grid-lines-vertical"></div>
                  <div className="grid-lines-horizontal"></div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Stage 2: Land Optimization */}
            <AnimatePresence>
              {stages[activeStage] === 'land' && (
                <motion.div
                  className="land-overlay"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.1 }}
                >
                  <div className="land-measurements">
                    <span>60'</span>
                    <span>40'</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Stage 3: Vastu Compass */}
            <AnimatePresence>
              {stages[activeStage] === 'vastu' && (
                <motion.div
                  className="vastu-compass-overlay"
                  initial={{ opacity: 0, rotate: -90 }}
                  animate={{ opacity: 1, rotate: 0 }}
                  exit={{ opacity: 0, rotate: 90 }}
                  transition={{ type: "spring", stiffness: 100 }}
                >
                  <div className="compass-ring"></div>
                  <div className="compass-directions">
                    <span>N</span><span>E</span><span>S</span><span>W</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Stage 4: Interior Furniture */}
            <AnimatePresence>
              {stages[activeStage] === 'interior' && (
                <motion.div
                  className="interior-furniture"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <Armchair size={48} strokeWidth={1.5} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Stage 5: Exterior Elements */}
            <AnimatePresence>
              {stages[activeStage] === 'exterior' && (
                <motion.div
                  className="exterior-elements"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <motion.div
                    className="tree-left"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <Trees size={40} />
                  </motion.div>
                  <motion.div
                    className="tree-right"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.4 }}
                  >
                    <Trees size={40} />
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>

          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <motion.div
          className="section-header"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={fadeInUp}
        >
          <h2>Why Choose Home Scope?</h2>
          <p>Everything you need to plan your perfect space</p>
        </motion.div>

        <motion.div
          className="features-grid"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          {/* Card 1: Land Rules Analysis & Optimization */}
          <TiltCard>
            <motion.div className="feature-card" variants={fadeInUp}>
              <div className="icon-wrapper">
                <Layout size={32} strokeWidth={1.5} />
              </div>
              <div className="card-content">
                <h3>Land Rules Analysis & Optimization</h3>
                <p>
                  Ensure your project complies with local zoning laws and building regulations instantly.
                  Our intelligent system analyzes your plot dimensions to generate optimized layouts that maximize usable area while adhering to setbacks, FAR, and coverage limits.
                </p>
              </div>
            </motion.div>
          </TiltCard>

          {/* Card 2: Vastu Correction */}
          <TiltCard>
            <motion.div className="feature-card" variants={fadeInUp}>
              <div className="icon-wrapper">
                <Compass size={32} strokeWidth={1.5} />
              </div>
              <div className="card-content">
                <h3>Vastu Correction</h3>
                <p>
                  Harmonize your living space with ancient wisdom.
                  Get detailed Vastu compliance reports and actionable remedies to align your home's energy flow, ensuring prosperity, health, and peace of mind.
                </p>
              </div>
            </motion.div>
          </TiltCard>

          {/* Card 3: Interior Optimization */}
          <TiltCard>
            <motion.div className="feature-card" variants={fadeInUp}>
              <div className="icon-wrapper">
                <Armchair size={32} strokeWidth={1.5} />
              </div>
              <div className="card-content">
                <h3>Interior Optimization</h3>
                <p>
                  Transform empty spaces into functional, beautiful living areas.
                  Our AI suggests optimal furniture placement, analyzes traffic flow, and ensures ergonomic design standards are met for every room in your home.
                </p>
              </div>
            </motion.div>
          </TiltCard>

          {/* Card 4: Exterior Optimization */}
          <TiltCard>
            <motion.div className="feature-card" variants={fadeInUp}>
              <div className="icon-wrapper">
                <Trees size={32} strokeWidth={1.5} />
              </div>
              <div className="card-content">
                <h3>Exterior Optimization</h3>
                <p>
                  Create stunning curb appeal and functional outdoor spaces.
                  From landscape design to efficient parking layouts and garden planning, we help you utilize every inch of your property's exterior effectively.
                </p>
              </div>
            </motion.div>
          </TiltCard>
        </motion.div>
      </section>


    </div>
  );
};

export default LandingPage;
