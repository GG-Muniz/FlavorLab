import { useState } from 'react';
import { Mail, Lock, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

export default function SignUp() {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }
      await register(email, password);
      // Auto-login and go to onboarding
      await login(email, password);
      navigate('/onboarding');
    } catch (e) {
      setError(e?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9fafb', padding: '16px' }}>
      <div style={{ background: '#fff', padding: 32, borderRadius: 16, width: '100%', maxWidth: 420, boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)', border: '1px solid #f3f4f6' }}>
        <h2 style={{ margin: 0, marginBottom: 8 }}>Create your account</h2>
        <p style={{ marginTop: 0, color: '#6b7280' }}>Start your HealthLab journey</p>

        {error && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Email</label>
            <div style={{ position: 'relative' }}>
              <Mail width={18} height={18} color="var(--icon-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" style={{ width: '100%', padding: '10px 12px 10px 38px', borderRadius: 10, border: '2px solid var(--input-border)', color: 'var(--text-primary)' }} />
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Password</label>
            <div style={{ position: 'relative' }}>
              <Lock width={18} height={18} color="var(--icon-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
              <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} placeholder="Minimum 8 characters" style={{ width: '100%', padding: '10px 44px 10px 38px', borderRadius: 10, border: '2px solid var(--input-border)', color: 'var(--text-primary)' }} />
              <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: 10, top: 8, background: 'transparent', border: 'none', cursor: 'pointer', padding: 4 }}>
                {showPassword ? <EyeOff width={18} height={18} color="var(--icon-muted)" /> : <Eye width={18} height={18} color="var(--icon-muted)" />}
              </button>
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Confirm Password</label>
            <div style={{ position: 'relative' }}>
              <Lock width={18} height={18} color="var(--icon-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
              <input type={showConfirm ? 'text' : 'password'} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={8} placeholder="Re-enter your password" style={{ width: '100%', padding: '10px 44px 10px 38px', borderRadius: 10, border: '2px solid var(--input-border)', color: 'var(--text-primary)' }} />
              <button type="button" onClick={() => setShowConfirm(!showConfirm)} style={{ position: 'absolute', right: 10, top: 8, background: 'transparent', border: 'none', cursor: 'pointer', padding: 4 }}>
                {showConfirm ? <EyeOff width={18} height={18} color="var(--icon-muted)" /> : <Eye width={18} height={18} color="var(--icon-muted)" />}
              </button>
            </div>
            {confirmPassword && password !== confirmPassword && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#b91c1c', fontSize: 13, marginTop: 6 }}>
                <AlertCircle width={16} height={16} />
                <span>Passwords do not match</span>
              </div>
            )}
          </div>

          <button type="submit" disabled={loading} style={{ width: '100%', padding: '12px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: 10, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div style={{ marginTop: 16, color: '#6b7280' }}>
          Already have an account? <Link to="/login" style={{ color: '#16a34a', fontWeight: 600 }}>Sign in</Link>
        </div>
      </div>
    </div>
  );
}


