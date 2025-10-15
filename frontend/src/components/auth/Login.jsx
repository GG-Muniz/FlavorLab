import { useRef, useState } from 'react';
import { Apple, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Login = ({ onLogin }) => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [error, setError] = useState('');
  const formRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      // Basic guard: ensure non-empty values before hitting API
      if (!email || !password) {
        setError('Please enter email and password');
        return;
      }
      await login(email, password);
      if (onLogin) onLogin();
      navigate('/');
    } catch (e) {
      setError(e?.message || 'Invalid credentials');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #bbf7d0 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px'
    }}>
      {/* Decorative background circles */}
      <div style={{
        position: 'absolute',
        top: '-10%',
        right: '-5%',
        width: '400px',
        height: '400px',
        background: 'rgba(34, 197, 94, 0.1)',
        borderRadius: '50%',
        filter: 'blur(80px)'
      }}></div>
      <div style={{
        position: 'absolute',
        bottom: '-10%',
        left: '-5%',
        width: '300px',
        height: '300px',
        background: 'rgba(34, 197, 94, 0.15)',
        borderRadius: '50%',
        filter: 'blur(60px)'
      }}></div>

      {/* Login Card */}
      <div style={{
        background: '#ffffff',
        borderRadius: '24px',
        padding: '48px',
        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        border: '1px solid #f3f4f6',
        width: '100%',
        maxWidth: '440px',
        position: 'relative',
        zIndex: 1
      }}>
        {/* Logo and Title */}
        <div style={{
          textAlign: 'center',
          marginBottom: '40px'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px',
            boxShadow: '0 10px 15px -3px rgb(34 197 94 / 0.4)'
          }}>
            <Apple width={40} height={40} color="#ffffff" strokeWidth={2.5} />
          </div>

          <h1 style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#111827',
            marginBottom: '8px',
            letterSpacing: '-0.025em'
          }}>
            Welcome to HealthLab
          </h1>

          <p style={{
            fontSize: '16px',
            color: '#6b7280',
            fontWeight: '400'
          }}>
            Sign in to continue your nutrition journey
          </p>
        </div>

        {/* Login Form */}
        <form ref={formRef} onSubmit={handleSubmit}>
          {params.get('registered') && (
            <div style={{ marginBottom: '16px', padding: '10px 12px', background: '#f0fdf4', border: '1px solid #bbf7d0', color: '#166534', borderRadius: 8 }}>
              Account created. Please sign in.
            </div>
          )}
          {error && (
            <div style={{ marginBottom: '16px', padding: '10px 12px', background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', borderRadius: 8 }}>
              {error}
            </div>
          )}
          {/* Email Input */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Email Address
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <div style={{
                position: 'absolute',
                left: '16px',
                display: 'flex',
                alignItems: 'center',
                pointerEvents: 'none'
              }}>
                <Mail width={20} height={20} color="#9ca3af" />
              </div>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                style={{
                  width: '100%',
                  padding: '14px 16px 14px 48px',
                  borderRadius: '12px',
                  border: '2px solid var(--input-border)',
                  fontSize: '15px',
                  color: 'var(--text-primary)',
                  transition: 'all 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--input-focus-border)';
                  e.target.style.boxShadow = '0 0 0 3px var(--focus-ring)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--input-border)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          {/* Password Input */}
          <div style={{ marginBottom: '32px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Password
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <div style={{
                position: 'absolute',
                left: '16px',
                display: 'flex',
                alignItems: 'center',
                pointerEvents: 'none'
              }}>
                <Lock width={20} height={20} color="#9ca3af" />
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); formRef.current?.requestSubmit(); } }}
                placeholder="Enter your password"
                style={{
                  width: '100%',
                  padding: '14px 48px 14px 48px',
                  borderRadius: '12px',
                  border: '2px solid var(--input-border)',
                  fontSize: '15px',
                  color: 'var(--text-primary)',
                  transition: 'all 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--input-focus-border)';
                  e.target.style.boxShadow = '0 0 0 3px var(--focus-ring)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--input-border)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '16px',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '4px'
                }}
              >
                {showPassword ? (
                  <EyeOff width={20} height={20} color="#9ca3af" />
                ) : (
                  <Eye width={20} height={20} color="#9ca3af" />
                )}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            style={{
              width: '100%',
              padding: '16px',
              background: isHovered
                ? 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)'
                : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: isHovered
                ? '0 10px 25px -5px rgb(34 197 94 / 0.5)'
                : '0 10px 15px -3px rgb(34 197 94 / 0.3)',
              transform: isHovered ? 'translateY(-2px)' : 'translateY(0)'
            }}
          >
            Sign In
          </button>
        </form>

        {/* Footer Links */}
        <div style={{
          marginTop: '32px',
          textAlign: 'center'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '14px',
            color: '#6b7280',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <Link
              to="/forgot-password"
              style={{
                color: '#22c55e',
                textDecoration: 'none',
                fontWeight: '500',
                transition: 'color 0.2s'
              }}
              onMouseEnter={(e) => e.target.style.color = '#16a34a'}
              onMouseLeave={(e) => e.target.style.color = '#22c55e'}
            >
              Forgot password?
            </Link>

            <div>
              Don't have an account?{' '}
              <Link
                to="/signup"
                style={{
                  color: '#22c55e',
                  textDecoration: 'none',
                  fontWeight: '600',
                  transition: 'color 0.2s'
                }}
                onMouseEnter={(e) => e.target.style.color = '#16a34a'}
                onMouseLeave={(e) => e.target.style.color = '#22c55e'}
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>

        {/* Info Badge removed after integration */}
      </div>
    </div>
  );
};

export default Login;
