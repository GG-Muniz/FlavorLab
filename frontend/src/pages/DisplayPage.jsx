import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext.jsx';

export default function DisplayPage() {
  const { theme, setTheme, toggleTheme } = useTheme();
  const [localTheme, setLocalTheme] = useState(theme);
  useEffect(() => { setLocalTheme(theme); }, [theme]);
  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-gray-50)', padding: 24 }}>
      <div style={{ maxWidth: 800, margin: '0 auto', background: 'var(--color-gray-100)', borderRadius: 16, padding: 24, border: '2px solid var(--color-gray-200)', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.15)' }}>
        <h2 style={{ marginTop: 0 }}>Display & Accessibility</h2>
        <p>Toggle appearance and accessibility preferences.</p>
        <div style={{ marginTop: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '10px 12px', borderRadius: 10, border: '2px solid var(--color-gray-200)', background: 'transparent', boxShadow: '0 4px 10px rgba(0,0,0,0.05)' }}>
            <input type="checkbox" checked={localTheme === 'dark'} onChange={(e) => { const next = e.target.checked ? 'dark' : 'light'; setLocalTheme(next); setTheme(next); }} />
            Dark Mode
          </label>
          <button onClick={toggleTheme} style={{ padding: '10px 12px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Toggle</button>
        </div>
      </div>
    </div>
  );
}


