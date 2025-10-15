import { useState } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import { changePassword as apiChangePassword, deleteMyAccount as apiDeleteMyAccount } from '../api/auth.js';

export default function SettingsPage() {
  const { token, logout } = useAuth();
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);

  async function changePassword(e) {
    e.preventDefault();
    setMessage('');
    setError('');
    if (!form.new_password || form.new_password !== form.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    setSaving(true);
    try {
      await apiChangePassword(token, form.current_password, form.new_password);
      setMessage('Password changed successfully');
      setForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setError(err?.message || 'Failed to change password');
    } finally {
      setSaving(false);
    }
  }

  async function deleteAccount() {
    setError('');
    setMessage('');
    try {
      await apiDeleteMyAccount(token);
      logout();
    } catch (err) {
      setError(err?.message || 'Failed to delete account');
    } finally {
      setConfirmOpen(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-gray-50)', padding: 24 }}>
      <div style={{ maxWidth: 800, margin: '0 auto', background: 'var(--color-gray-100)', borderRadius: 16, padding: 24, border: '2px solid var(--color-gray-200)', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.15)' }}>
        <h2 style={{ marginTop: 0 }}>Settings & Privacy</h2>
        {message && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#ecfdf5', color: '#065f46', border: '1px solid #a7f3d0', borderRadius: 8 }}>{message}</div>}
        {error && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>}

        <section style={{ marginBottom: 32 }}>
          <h3 style={{ margin: '0 0 12px 0' }}>Change Password</h3>
          <form onSubmit={changePassword} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, border: '2px solid var(--color-gray-200)', borderRadius: 12, padding: 16, boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Current Password</label>
              <input type="password" value={form.current_password} onChange={(e) => setForm({ ...form, current_password: e.target.value })} style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid var(--color-gray-200)', background: 'transparent' }} />
            </div>
            <div />
            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>New Password</label>
              <input type="password" value={form.new_password} onChange={(e) => setForm({ ...form, new_password: e.target.value })} style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid var(--color-gray-200)', background: 'transparent' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Confirm New Password</label>
              <input type="password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid var(--color-gray-200)', background: 'transparent' }} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <button type="submit" disabled={saving} style={{ padding: '10px 16px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: saving ? 'not-allowed' : 'pointer' }}>
                {saving ? 'Saving...' : 'Update Password'}
              </button>
            </div>
          </form>
        </section>

        <section>
          <h3 style={{ margin: '0 0 12px 0', color: '#b91c1c' }}>Danger Zone</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 16, background: 'rgba(255, 87, 34, 0.06)', border: '2px solid #ea580c', borderRadius: 12, boxShadow: '0 8px 20px rgba(234,88,12,0.15)' }}>
            <div>
              <div style={{ fontWeight: 700, color: '#7c2d12' }}>Delete Account</div>
              <div style={{ color: '#9a3412', fontSize: 14 }}>This action cannot be undone.</div>
            </div>
            <button onClick={() => setConfirmOpen(true)} style={{ padding: '8px 12px', borderRadius: 10, background: '#ef4444', color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Delete Account</button>
          </div>
        </section>

        {confirmOpen && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <div style={{ background: 'var(--color-gray-100)', padding: 24, borderRadius: 12, width: 420, border: '2px solid var(--color-gray-200)', boxShadow: '0 20px 40px rgba(0,0,0,0.25)' }}>
              <h3 style={{ marginTop: 0 }}>Confirm Deletion</h3>
              <p>Are you sure you want to delete your account? This cannot be undone.</p>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                <button onClick={() => setConfirmOpen(false)} style={{ padding: '8px 12px', borderRadius: 8, background: 'transparent', border: '2px solid var(--color-gray-200)' }}>Cancel</button>
                <button onClick={deleteAccount} style={{ padding: '8px 12px', borderRadius: 8, background: '#ef4444', color: '#fff', border: 'none', fontWeight: 700 }}>Delete</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


