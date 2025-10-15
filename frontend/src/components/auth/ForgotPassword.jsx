import { useState } from 'react';
import { Link } from 'react-router-dom';
import { requestPasswordReset } from '../../api/auth';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await requestPasswordReset(email);
      setSuccess('If the email exists, a reset link has been sent. Check server logs for the link in this MVP.');
    } catch (e) {
      setError(e?.message || 'Failed to request password reset');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9fafb', padding: '16px' }}>
      <div style={{ background: '#fff', padding: 32, borderRadius: 16, width: '100%', maxWidth: 480, boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)', border: '1px solid #f3f4f6' }}>
        <h2 style={{ marginTop: 0 }}>Password reset</h2>
        <p style={{ color: '#6b7280' }}>Enter your email. If an account exists, we'll send a reset link.</p>

        {success && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', borderRadius: 8 }}>{success}</div>
        )}
        {error && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid var(--input-border)', color: 'var(--text-primary)' }} />
          <button type="submit" disabled={loading} style={{ marginTop: 12, width: '100%', padding: '12px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: 10, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <div style={{ marginTop: 16 }}>
          <Link to="/login" style={{ color: '#16a34a', fontWeight: 600 }}>Back to Sign in</Link>
        </div>
      </div>
    </div>
  );
}


