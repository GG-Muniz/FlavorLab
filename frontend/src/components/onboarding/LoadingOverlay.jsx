import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const LoadingOverlay = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999
      }}
    >
      <motion.div
        style={{
          background: '#ffffff',
          borderRadius: '24px',
          padding: '48px 64px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '24px'
        }}
      >
        {/* Logo with pulse animation */}
        <motion.div
          animate={{
            scale: [1, 1.05, 1]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
          style={{
            width: '80px',
            height: '80px',
            borderRadius: '20px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 10px 25px -5px rgba(34, 197, 94, 0.3)'
          }}
        >
          <img src="/Healthlab.png" alt="HealthLab" onError={(e)=>{ e.currentTarget.src='/favicon.png'; }} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </motion.div>

        {/* Loading text with fade animation */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          style={{
            textAlign: 'center'
          }}
        >
          <h3 style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#111827',
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>
            Crafting your plan...
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            This will only take a moment
          </p>
        </motion.div>

        {/* Animated dots */}
        <div style={{
          display: 'flex',
          gap: '8px',
          alignItems: 'center'
        }}>
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
                ease: 'easeInOut'
              }}
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#22c55e'
              }}
            />
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default LoadingOverlay;
