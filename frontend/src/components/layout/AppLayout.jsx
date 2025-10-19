import { Outlet, Link } from 'react-router-dom';
import { Apple, BookOpen } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import ProfileDropdown from '../profile/ProfileDropdown';
import { absoluteUrl } from '../../api/auth';

export default function AppLayout() {
  const { user } = useAuth();
  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-gray-50)' }}>
      <header style={{ background: 'var(--color-gray-100)', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)', borderBottom: '2px solid var(--color-gray-200)' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px' }}>
          <Link to="/?tab=dashboard" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
            <div style={{ width: 40, height: 40, background: '#22c55e', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)' }}>
              <Apple width={24} height={24} color="#ffffff" strokeWidth={2.5} />
            </div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--color-gray-900)', letterSpacing: '-0.025em', margin: 0 }}>HealthLab</h1>
          </Link>

          <nav style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Link to="/ingredients" style={{
              display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none',
              padding: '8px 12px', borderRadius: 10, border: '1px solid var(--color-gray-200)'
            }}>
              <BookOpen width={18} height={18} color="#111827" />
              <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>Ingredients</span>
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


