import { Outlet, Link, useLocation } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import ProfileDropdown from '../profile/ProfileDropdown';
import { absoluteUrl } from '../../api/auth';

export default function AppLayout() {
  const { user } = useAuth();
  const location = useLocation();

  const navLinkStyle = (path) => {
    const isActive = location.pathname.startsWith(path);
    return {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      textDecoration: 'none',
      padding: '8px 12px',
      borderRadius: 10,
      border: `1px solid ${isActive ? 'var(--color-gray-300)' : 'var(--color-gray-200)'}`,
      background: isActive ? 'var(--color-gray-200)' : 'transparent',
      color: isActive ? 'var(--color-gray-900)' : 'var(--text-primary)',
      transition: 'background 0.2s ease, border-color 0.2s ease',
    };
  };

  const navLabelStyle = (path) => ({
    fontSize: 14,
    fontWeight: 600,
    color: location.pathname.startsWith(path) ? 'var(--color-gray-900)' : 'var(--text-primary)'
  });

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-gray-50)' }}>
      <header style={{ background: 'var(--color-gray-100)', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)', borderBottom: '2px solid var(--color-gray-200)' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px' }}>
          <Link to="/?tab=dashboard" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
            <img src="/Healthlab.png" alt="HealthLab" onError={(e)=>{ e.currentTarget.src='/favicon.png'; }} style={{ width: 40, height: 40, borderRadius: 10, boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)', objectFit: 'cover' }} />
            <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--color-gray-900)', letterSpacing: '-0.025em', margin: 0 }}>HealthLab</h1>
          </Link>

          <nav style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Link to="/ingredients" style={navLinkStyle('/ingredients')}>
              <BookOpen width={18} height={18} color="#111827" />
              <span style={navLabelStyle('/ingredients')}>Ingredients</span>
            </Link>
          </nav>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Hello, <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{user?.first_name || user?.email}</span> 👋</div>
            <ProfileDropdown avatarUrl={user?.avatar_url ? absoluteUrl(user.avatar_url) : undefined} />
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}


