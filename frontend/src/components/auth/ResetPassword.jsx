import { useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { resetPassword } from '../../api/auth';
import { Eye, EyeOff } from 'lucide-react';

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!token) {
      setError('Invalid or missing token');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await resetPassword(token, password);
      setSuccess('Password reset successfully. Redirecting to sign in...');
      setTimeout(() => navigate('/login?reset=1'), 1200);
    } catch (e) {
      setError(e?.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9fafb', padding: '16px' }}>
      <div style={{ background: '#fff', padding: 32, borderRadius: 16, width: '100%', maxWidth: 480, boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)', border: '1px solid #f3f4f6' }}>
        <h2 style={{ marginTop: 0 }}>Set a new password</h2>

        {success && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', borderRadius: 8 }}>{success}</div>
        )}
        {error && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>New Password</label>
          <div style={{ position: 'relative' }}>
            <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} placeholder="Minimum 8 characters" style={{ width: '100%', padding: '10px 40px 10px 12px', borderRadius: 10, border: '2px solid var(--input-border)', color: 'var(--text-primary)' }} />
            <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: 10, top: 8, background: 'transparent', border: 'none', cursor: 'pointer', padding: 4 }}>
              {showPassword ? <EyeOff width={18} height={18} color="var(--icon-muted)" /> : <Eye width={18} height={18} color="var(--icon-muted)" />}
            </button>
          </div>

          <label style={{ display: 'block', marginBottom: 6, marginTop: 12, fontWeight: 600 }}>Confirm Password</label>
          <div style={{ position: 'relative' }}>
            <input type={showConfirm ? 'text' : 'password'} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={8} placeholder="Re-enter your password" style={{ width: '100%', padding: '10px 40px 10px 12px', borderRadius: 10, border: '2px solid var(--input-border)', color: 'var(--text-primary)' }} />
            <button type="button" onClick={() => setShowConfirm(!showConfirm)} style={{ position: 'absolute', right: 10, top: 8, background: 'transparent', border: 'none', cursor: 'pointer', padding: 4 }}>
              {showConfirm ? <EyeOff width={18} height={18} color="var(--icon-muted)" /> : <Eye width={18} height={18} color="var(--icon-muted)" />}
            </button>
          </div>

          <button type="submit" disabled={loading} style={{ marginTop: 12, width: '100%', padding: '12px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: 10, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? 'Saving...' : 'Reset Password'}
          </button>
        </form>

        <div style={{ marginTop: 16 }}>
          <Link to="/login" style={{ color: '#16a34a', fontWeight: 600 }}>Back to Sign in</Link>
        </div>
      </div>
    </div>
  );
}


