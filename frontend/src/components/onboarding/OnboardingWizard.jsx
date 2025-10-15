import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { updateUserProfile, getCurrentUser } from '../../api/auth';
import { useNavigate } from 'react-router-dom';
import NutriTest from './NutriTest';

export default function OnboardingWizard({ onComplete }) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(2); // starting at personal info step
  const [units, setUnits] = useState('metric'); // 'metric' | 'imperial'
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [age, setAge] = useState('');
  // Metric fields (single input in centimeters)
  const [heightCm, setHeightCm] = useState('');
  const [weightKg, setWeightKg] = useState('');
  // Imperial fields
  const [heightFt, setHeightFt] = useState('');
  const [heightIn, setHeightIn] = useState('');
  const [weightLb, setWeightLb] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  function toCmFromImperial(ftStr, inStr) {
    const ft = parseFloat(ftStr || '0');
    const inches = parseFloat(inStr || '0');
    const totalInches = ft * 12 + inches;
    const cm = totalInches * 2.54;
    return Math.max(0, Math.round(cm));
  }

  function toKgFromLb(lbStr) {
    const lb = parseFloat(lbStr || '0');
    return Math.max(0, Math.round((lb * 0.45359237) * 10) / 10);
  }

  async function handleSavePersonalInfo(e) {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      let height_cm;
      let weight_kg;
      if (units === 'metric') {
        height_cm = heightCm ? parseInt(heightCm, 10) : 0;
        weight_kg = weightKg ? parseFloat(weightKg) : 0;
      } else {
        height_cm = toCmFromImperial(heightFt, heightIn);
        weight_kg = toKgFromLb(weightLb);
      }
      const payload = {
        first_name: firstName || undefined,
        last_name: lastName || undefined,
        age: age ? parseInt(age, 10) : undefined,
        height_cm,
        weight_kg
      };
      await updateUserProfile(token, payload);
      setStep(3);
    } catch (err) {
      setError(err?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  if (step === 2) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #bbf7d0 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px'
      }}>
        <div style={{ background: '#ffffff', borderRadius: 24, padding: 32, border: '1px solid #f3f4f6', width: '100%', maxWidth: 520, boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)' }}>
          <h2 style={{ marginTop: 0, marginBottom: 12 }}>Personal information</h2>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontWeight: 600, marginRight: 12 }}>Units</label>
            <button type="button" onClick={() => setUnits('metric')} style={{ padding: '6px 10px', marginRight: 6, borderRadius: 8, border: '1px solid #e5e7eb', background: units==='metric' ? '#dcfce7' : '#fff' }}>Metric (m, cm, kg)</button>
            <button type="button" onClick={() => setUnits('imperial')} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #e5e7eb', background: units==='imperial' ? '#dcfce7' : '#fff' }}>Imperial (ft+in, lb)</button>
          </div>

          {error && (
            <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>
          )}

          <form onSubmit={handleSavePersonalInfo}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>First name</label>
                <input value={firstName} onChange={(e) => setFirstName(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Last name</label>
                <input value={lastName} onChange={(e) => setLastName(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Age (years)</label>
                <input type="number" min="0" max="130" value={age} onChange={(e) => setAge(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
              </div>
              {units === 'metric' ? (
                <div>
                  <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Height (cm)</label>
                  <input type="number" min="0" value={heightCm} onChange={(e) => setHeightCm(e.target.value)} placeholder="e.g., 175" style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
                </div>
              ) : (
                <div>
                  <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Height</label>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                    <input type="number" min="0" value={heightFt} onChange={(e) => setHeightFt(e.target.value)} placeholder="ft" style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
                    <input type="number" min="0" value={heightIn} onChange={(e) => setHeightIn(e.target.value)} placeholder="in" style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
                  </div>
                </div>
              )}
            </div>

            <div style={{ marginTop: 12 }}>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Weight</label>
              {units === 'metric' ? (
                <input type="number" min="0" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} placeholder="kg" style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
              ) : (
                <input type="number" min="0" value={weightLb} onChange={(e) => setWeightLb(e.target.value)} placeholder="lb" style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #e5e7eb' }} />
              )}
            </div>

            <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
              <button type="submit" disabled={saving} style={{ padding: '10px 16px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: 10, fontWeight: 700, cursor: saving ? 'not-allowed' : 'pointer' }}>
                {saving ? 'Saving...' : 'Save & Continue'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Step 3 - integrate goals selection and persist
  if (step === 3) {
    async function handleGoalsComplete({ selectedGoals }) {
      try {
        let existing = {};
        try {
          const me = await getCurrentUser(token);
          existing = me?.preferences || {};
        } catch {}
        await updateUserProfile(token, { preferences: { ...existing, health_goals: selectedGoals } });
      } catch {}
      if (onComplete) onComplete();
      navigate('/');
    }

    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #bbf7d0 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px'
      }}>
        <div style={{ background: '#fff', borderRadius: 24, padding: 32, border: '1px solid #f3f4f6', width: '100%', maxWidth: 1000, boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)' }}>
          <NutriTest onComplete={handleGoalsComplete} />
        </div>
      </div>
    );
  }

  return null;
}


