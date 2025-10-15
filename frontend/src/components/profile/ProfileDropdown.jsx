import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { User as UserIcon, Settings, HelpCircle, SunMoon, LogOut, ChevronRight } from 'lucide-react';

export default function ProfileDropdown({ avatarUrl }) {
  const { logout, user } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const fullName = (() => {
    const first = (user?.first_name || '').trim();
    const last = (user?.last_name || '').trim();
    if (first && last) return `${first} ${last}`;
    return first || last || user?.email || 'User';
  })();

  const itemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '10px 12px',
    borderRadius: 10,
    color: 'var(--text-primary)',
    textDecoration: 'none',
    cursor: 'pointer'
  };

  const itemHoverBg = 'rgba(148, 163, 184, 0.15)';

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button onClick={() => setOpen(!open)} style={{
        width: 36, height: 36, borderRadius: '50%', border: '2px solid #bbf7d0',
        background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden'
      }}>
        {avatarUrl ? (
          <img src={avatarUrl} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
        ) : (
          <span style={{ fontSize: 14, color: '#15803d', fontWeight: 700 }}>
            {(user?.first_name?.[0] || user?.email?.[0] || '?').toUpperCase()}
          </span>
        )}
      </button>
      {open && (
        <div style={{ position: 'absolute', right: 0, top: 'calc(100% + 8px)', background: 'var(--color-gray-100)', borderRadius: 16, boxShadow: '0 24px 48px -12px rgba(0,0,0,0.6)', border: '2px solid var(--color-gray-200)', minWidth: 260, padding: 8, zIndex: 50 }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12, borderRadius: 12, background: 'var(--color-gray-50)', border: '2px solid var(--color-gray-200)', margin: 4, boxShadow: '0 6px 16px rgba(0,0,0,0.25)' }}>
            <div style={{ width: 40, height: 40, borderRadius: '50%', overflow: 'hidden', background: '#f0fdf4', border: '2px solid #bbf7d0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {avatarUrl ? (
                <img src={avatarUrl} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <span style={{ fontSize: 14, color: '#15803d', fontWeight: 700 }}>
                  {(user?.first_name?.[0] || user?.email?.[0] || '?').toUpperCase()}
                </span>
              )}
            </div>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{fullName}</div>
              {user?.email && <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{user.email}</div>}
            </div>
          </div>
          <div style={{ height: 8 }} />
          {/* Menu */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: 4 }}>
            <Link to="/profile" onClick={() => setOpen(false)}
              style={itemStyle}
              onMouseEnter={(e) => { e.currentTarget.style.background = itemHoverBg; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <UserIcon size={18} color="var(--text-primary)" />
              <span style={{ flex: 1 }}>Edit Profile</span>
              <ChevronRight size={16} color="var(--icon-muted)" />
            </Link>

            <Link to="/settings" onClick={() => setOpen(false)}
              style={itemStyle}
              onMouseEnter={(e) => { e.currentTarget.style.background = itemHoverBg; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <Settings size={18} color="var(--text-primary)" />
              <span style={{ flex: 1 }}>Settings & Privacy</span>
              <ChevronRight size={16} color="var(--icon-muted)" />
            </Link>

            <Link to="/help" onClick={() => setOpen(false)}
              style={itemStyle}
              onMouseEnter={(e) => { e.currentTarget.style.background = itemHoverBg; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <HelpCircle size={18} color="var(--text-primary)" />
              <span style={{ flex: 1 }}>Help</span>
              <ChevronRight size={16} color="var(--icon-muted)" />
            </Link>

            <Link to="/display" onClick={() => setOpen(false)}
              style={itemStyle}
              onMouseEnter={(e) => { e.currentTarget.style.background = itemHoverBg; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <SunMoon size={18} color="var(--text-primary)" />
              <span style={{ flex: 1 }}>Display & Accessibility</span>
              <ChevronRight size={16} color="var(--icon-muted)" />
            </Link>

            <div style={{ height: 4 }} />
            <button
              onClick={() => { logout(); setOpen(false); }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                width: '100%',
                padding: '10px 12px',
                borderRadius: 10,
                border: '2px solid var(--destructive-border)',
                background: 'var(--destructive-bg)',
                color: 'var(--destructive-text)',
                fontWeight: 700,
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.boxShadow = '0 4px 10px rgba(239,68,68,0.25)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.boxShadow = 'none'; }}
            >
              <LogOut size={18} color="var(--destructive-text)" />
              <span style={{ flex: 1 }}>Log Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


