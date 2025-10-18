import { motion } from 'framer-motion';
import './cards.css';

export function BackgroundCard({ tone = 'neutral', children, style = {} }) {
  const toneClass = tone === 'blue' ? 'fl-bg-blue' : tone === 'green' ? 'fl-bg-green' : 'fl-bg-neutral';
  return (
    <div className={`fl-background-card ${toneClass}`} style={style}>
      {children}
    </div>
  );
}

export function SectionHeader({ icon, title, subtitle, iconBg = '#f0fdf4', iconColor = '#16a34a' }) {
  return (
    <div className="fl-section-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
        <div style={{ width: 32, height: 32, background: iconBg, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {icon && icon({ width: 20, height: 20, color: iconColor })}
        </div>
        <h3 style={{ fontSize: 20, fontWeight: 700, color: '#000000', margin: 0 }}>{title}</h3>
      </div>
      {subtitle && <p style={{ fontSize: 14, color: '#000000', margin: 0 }}>{subtitle}</p>}
    </div>
  );
}

export function SelectableCard({ palette = 'green', selected = false, onClick, emoji, title, subtitle }) {
  const paletteClass = palette === 'orange' ? 'fl-palette-orange' : palette === 'green' ? 'fl-palette-green' : 'fl-palette-neutral';
  const selectedColor = selected ? (palette === 'green' ? '#166534' : (palette === 'orange' ? '#b45309' : undefined)) : undefined;
  const titleStyle = selectedColor ? { color: selectedColor } : undefined;
  const subtitleStyle = selectedColor ? { color: selectedColor } : undefined;

  return (
    <motion.div
      className={`fl-selectable-card ${paletteClass} ${selected ? 'fl-selected' : ''}`}
      onClick={onClick}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
    >
      <span style={{ fontSize: 40, marginBottom: 8 }}>{emoji}</span>
      <span className="fl-title" style={titleStyle}>{title}</span>
      {subtitle && <span className="fl-subtitle" style={subtitleStyle}>{subtitle}</span>}
    </motion.div>
  );
}


