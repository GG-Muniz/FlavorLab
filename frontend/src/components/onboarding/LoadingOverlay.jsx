import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const LoadingOverlay = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2000
      }}
    >
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        style={{
          width: '320px',
          padding: '32px 28px',
          borderRadius: '24px',
          background: 'rgba(255, 255, 255, 0.95)',
          boxShadow: '0 25px 50px -12px rgba(16, 185, 129, 0.45)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px'
        }}
      >
        <motion.div
          animate={{ scale: [1, 1.08, 1], rotate: [0, 3, -3, 0] }}
          transition={{ duration: 2.2, repeat: Infinity, repeatType: 'reverse' }}
          style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 10px 25px -5px rgba(34, 197, 94, 0.3)'
          }}
        >
          <Sparkles width={40} height={40} color="#ffffff" strokeWidth={2.5} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          style={{ textAlign: 'center' }}
        >
          <div style={{ fontSize: 20, fontWeight: 700, color: '#0f172a' }}>Crafting your experience</div>
          <div style={{ fontSize: 14, color: '#475569', marginTop: 6 }}>Personalizing everything to your nutrition goals...</div>
        </motion.div>

        <motion.div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {[0, 1, 2].map((dot) => (
            <motion.span
              key={dot}
              animate={{ opacity: [0.2, 1, 0.2] }}
              transition={{ duration: 1.2, repeat: Infinity, delay: dot * 0.2 }}
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background: '#16a34a'
              }}
            />
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default LoadingOverlay;
