import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { uploadAvatar, absoluteUrl } from '../../api/auth';
import GoalsPreferencesForm from './GoalsPreferencesForm.jsx';

export default function ProfilePage() {
  const { user, token, updateProfile, refreshUser } = useAuth();
  const location = useLocation();
  const inputRef = useRef(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState(location.state?.defaultTab || 'personal'); // 'personal' | 'goals'
  const [unitSystem, setUnitSystem] = useState('metric'); // 'metric' | 'imperial'
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    height_cm: '',
    weight_kg: '',
    gender: '',
    activity_level: '',
  });
  // Imperial render states
  const [heightFt, setHeightFt] = useState('');
  const [heightIn, setHeightIn] = useState('');
  const [weightLb, setWeightLb] = useState('');

  const CM_TO_IN = 0.393701;
  const KG_TO_LB = 2.20462;
  const inToCm = (ft, inches) => {
    const totalIn = (parseInt(ft || '0', 10) * 12) + parseInt(inches || '0', 10);
    return Math.max(0, Math.round(totalIn / CM_TO_IN));
  };
  const cmToFeetInches = (cm) => {
    const totalIn = (parseInt(cm || '0', 10)) * CM_TO_IN;
    const ft = Math.floor(totalIn / 12);
    const inches = Math.round(totalIn % 12);
    return { ft: String(ft), inches: String(inches) };
  };
  const kgToLb = (kg) => (kg === '' || kg == null ? '' : (Math.round(parseFloat(kg) * KG_TO_LB * 10) / 10).toString());
  const lbToKg = (lb) => (lb === '' || lb == null ? '' : (Math.round((parseFloat(lb) / KG_TO_LB) * 10) / 10));

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        date_of_birth: user.date_of_birth ? String(user.date_of_birth).slice(0, 10) : '',
        height_cm: user.height_cm ?? '',
        weight_kg: user.weight_kg ?? '',
        gender: user.gender || '',
        activity_level: user.activity_level || '',
      });
      // Initialize imperial fields from metric
      const { ft, inches } = cmToFeetInches(user.height_cm ?? 0);
      setHeightFt(ft);
      setHeightIn(inches);
      setWeightLb(kgToLb(user.weight_kg ?? ''));
    }
  }, [user]);

  async function onFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError('');
    setSaving(true);
    try {
      await uploadAvatar(token, file);
      await refreshUser();
    } catch (err) {
      setError(err?.message || 'Failed to upload');
    } finally {
      setSaving(false);
    }
  }

  async function onSaveProfile(e) {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      // Convert if imperial is selected
      const metricHeight = unitSystem === 'imperial' ? inToCm(heightFt, heightIn) : (form.height_cm !== '' ? parseInt(form.height_cm, 10) : undefined);
      const metricWeight = unitSystem === 'imperial' ? lbToKg(weightLb) : (form.weight_kg !== '' ? parseFloat(form.weight_kg) : undefined);
      const payload = {
        first_name: form.first_name || undefined,
        last_name: form.last_name || undefined,
        height_cm: metricHeight,
        weight_kg: metricWeight,
        gender: form.gender || undefined,
        activity_level: form.activity_level || undefined,
        date_of_birth: form.date_of_birth || undefined,
      };
      await updateProfile(payload);
    } catch (err) {
      setError(err?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-gray-50)', padding: 24 }}>
      <div style={{ maxWidth: 800, margin: '0 auto', background: 'var(--color-gray-100)', borderRadius: 16, padding: 24, border: '2px solid var(--color-gray-200)', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.15)' }}>
        <h2 style={{ marginTop: 0 }}>Your Profile</h2>
        <div style={{ display: 'flex', gap: 8, margin: '12px 0 20px 0' }}>
          <button onClick={() => setActiveTab('personal')} style={{ padding: '8px 12px', borderRadius: 10, border: activeTab==='personal' ? '2px solid #22c55e' : '2px solid var(--color-gray-200)', background: activeTab==='personal' ? 'rgba(34,197,94,0.12)' : 'transparent', color: 'var(--text-primary)', fontWeight: 700, cursor: 'pointer' }}>Personal Info</button>
          <button onClick={() => setActiveTab('goals')} style={{ padding: '8px 12px', borderRadius: 10, border: activeTab==='goals' ? '2px solid #22c55e' : '2px solid var(--color-gray-200)', background: activeTab==='goals' ? 'rgba(34,197,94,0.12)' : 'transparent', color: 'var(--text-primary)', fontWeight: 700, cursor: 'pointer' }}>Goals & Preferences</button>
        </div>
        {error && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>}
        {activeTab === 'personal' && (
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ width: 96, height: 96, borderRadius: '50%', overflow: 'hidden', border: '2px solid #bbf7d0', background: '#f0fdf4' }}>
            {user?.avatar_url ? (
              <img src={absoluteUrl(user.avatar_url)} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#15803d', fontWeight: 700, fontSize: 32 }}>
                {(user?.first_name?.[0] || user?.email?.[0] || '?').toUpperCase()}
              </div>
            )}
          </div>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>{user?.first_name || user?.email}</div>
            <div style={{ color: 'var(--text-secondary)' }}>{user?.email}</div>
            <div style={{ marginTop: 12 }}>
              <button onClick={() => inputRef.current?.click()} disabled={saving} style={{ padding: '8px 12px', borderRadius: 8, background: '#22c55e', border: 'none', color: '#fff', fontWeight: 600, cursor: saving ? 'not-allowed' : 'pointer' }}>
                {saving ? 'Uploading...' : 'Upload New Picture'}
              </button>
              <input ref={inputRef} type="file" accept="image/png,image/jpeg,image/webp" onChange={onFileChange} style={{ display: 'none' }} />
            </div>
          </div>
        </div>
        )}
        {activeTab === 'personal' && (
        <form onSubmit={onSaveProfile} style={{ marginTop: 24, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, border: '2px solid var(--color-gray-200)', borderRadius: 12, padding: 16, boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>First name</label>
            <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Last name</label>
            <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Date of birth</label>
            <input type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Gender</label>
            <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} style={{ width: '100%' }}>
              <option value="">Select</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Activity level</label>
            <select value={form.activity_level} onChange={(e) => setForm({ ...form, activity_level: e.target.value })} style={{ width: '100%' }}>
              <option value="">Select</option>
              <option value="sedentary">Sedentary</option>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="active">Active</option>
              <option value="very_active">Very active</option>
            </select>
          </div>
          <div style={{ gridColumn: '1 / -1', marginTop: 8 }}>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Units</label>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="button" onClick={() => setUnitSystem('metric')} style={{ padding: '6px 10px', borderRadius: 8, border: '2px solid var(--input-border)', background: unitSystem==='metric' ? 'rgba(34,197,94,0.15)' : 'transparent', color: 'var(--text-primary)', fontWeight: 600 }}>Metric</button>
              <button type="button" onClick={() => setUnitSystem('imperial')} style={{ padding: '6px 10px', borderRadius: 8, border: '2px solid var(--input-border)', background: unitSystem==='imperial' ? 'rgba(34,197,94,0.15)' : 'transparent', color: 'var(--text-primary)', fontWeight: 600 }}>Imperial</button>
            </div>
          </div>
          {unitSystem === 'metric' ? (
            <>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Height (cm)</label>
                <input type="number" min="0" value={form.height_cm} onChange={(e) => setForm({ ...form, height_cm: e.target.value })} style={{ width: '100%' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Weight (kg)</label>
                <input type="number" min="0" step="0.1" value={form.weight_kg} onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} style={{ width: '100%' }} />
              </div>
            </>
          ) : (
            <>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Height</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  <input type="number" min="0" value={heightFt} onChange={(e) => setHeightFt(e.target.value)} placeholder="ft" style={{ width: '100%' }} />
                  <input type="number" min="0" value={heightIn} onChange={(e) => setHeightIn(e.target.value)} placeholder="in" style={{ width: '100%' }} />
                </div>
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Weight (lb)</label>
                <input type="number" min="0" step="0.1" value={weightLb} onChange={(e) => setWeightLb(e.target.value)} placeholder="lb" style={{ width: '100%' }} />
              </div>
            </>
          )}
          <div style={{ gridColumn: '1 / -1', marginTop: 8 }}>
            <button type="submit" disabled={saving} style={{ padding: '10px 16px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: saving ? 'not-allowed' : 'pointer' }}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
        )}
        {activeTab === 'goals' && (
          <div style={{ marginTop: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Goals & Preferences</div>
              <Link to="/nutritest" style={{ textDecoration: 'none' }}>
                <button style={{ padding: '10px 16px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer' }}>
                  Retake NutriTest
                </button>
              </Link>
            </div>
            <GoalsPreferencesForm onSaved={refreshUser} />
          </div>
        )}
      </div>
    </div>
  );
}


