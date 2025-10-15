import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { updateUserProfile } from '../../api/auth';

const PRESET_GOALS = [
  { key: 'weight_loss', label: 'Weight Loss' },
  { key: 'muscle_gain', label: 'Muscle Gain' },
  { key: 'improve_gut_health', label: 'Improve Gut Health' },
  { key: 'better_energy', label: 'Better Energy' }
];

const DIETS = ['', 'Balanced', 'Vegan', 'Vegetarian', 'Keto', 'Paleo', 'Pescetarian'];
const ALLERGENS = ['Dairy', 'Gluten', 'Peanuts', 'Tree Nuts', 'Shellfish', 'Soy', 'Eggs'];

export default function GoalsPreferencesForm({ onSaved }) {
  const { user, token } = useAuth();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const initialGoals = user?.health_goals || {};
  const initialPrefs = user?.dietary_preferences || {};

  const [goals, setGoals] = useState(() => {
    const map = {};
    PRESET_GOALS.forEach(g => { map[g.key] = Boolean(initialGoals?.[g.key]); });
    return map;
  });

  const [diet, setDiet] = useState(initialPrefs?.diet || '');
  const [allergies, setAllergies] = useState(new Set(initialPrefs?.allergies || []));
  const [disliked, setDisliked] = useState(initialPrefs?.disliked || []);
  const [tagInput, setTagInput] = useState('');

  function toggleAllergy(item) {
    const next = new Set(allergies);
    if (next.has(item)) next.delete(item); else next.add(item);
    setAllergies(next);
  }

  function addTag(e) {
    e?.preventDefault();
    const val = (tagInput || '').trim();
    if (!val) return;
    if (!disliked.includes(val)) setDisliked([...disliked, val]);
    setTagInput('');
  }

  function removeTag(idx) {
    const next = [...disliked];
    next.splice(idx, 1);
    setDisliked(next);
  }

  async function save() {
    setSaving(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        health_goals: goals,
        dietary_preferences: {
          diet,
          allergies: Array.from(allergies),
          disliked
        }
      };
      await updateUserProfile(token, payload);
      setMessage('Goals & preferences saved');
      onSaved && onSaved();
    } catch (err) {
      setError(err?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ border: '2px solid var(--color-gray-200)', borderRadius: 12, padding: 16, background: 'var(--color-gray-100)', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
      <h3 style={{ marginTop: 0 }}>Goals & Preferences</h3>
      {message && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#ecfdf5', color: '#065f46', border: '1px solid #a7f3d0', borderRadius: 8 }}>{message}</div>}
      {error && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Health Goals</div>
          <div style={{ display: 'grid', gap: 8 }}>
            {PRESET_GOALS.map(g => (
              <label key={g.key} style={{ display: 'flex', alignItems: 'center', gap: 8, border: '2px solid var(--color-gray-200)', borderRadius: 10, padding: '8px 10px', background: 'transparent' }}>
                <input type="checkbox" checked={!!goals[g.key]} onChange={(e) => setGoals({ ...goals, [g.key]: e.target.checked })} />
                {g.label}
              </label>
            ))}
          </div>
        </div>

        <div>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Dietary Plan</div>
          <select value={diet} onChange={(e) => setDiet(e.target.value)} style={{ width: '100%' }}>
            {DIETS.map(d => <option key={d} value={d}>{d || 'Select'}</option>)}
          </select>

          <div style={{ fontWeight: 700, margin: '16px 0 8px 0' }}>Allergies / Intolerances</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 8 }}>
            {ALLERGENS.map(a => (
              <label key={a} style={{ display: 'flex', alignItems: 'center', gap: 8, border: '2px solid var(--color-gray-200)', borderRadius: 10, padding: '8px 10px', background: 'transparent' }}>
                <input type="checkbox" checked={allergies.has(a)} onChange={() => toggleAllergy(a)} />
                {a}
              </label>
            ))}
          </div>

          <div style={{ fontWeight: 700, margin: '16px 0 8px 0' }}>Disliked Ingredients</div>
          <form onSubmit={addTag} style={{ display: 'flex', gap: 8 }}>
            <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} placeholder="Add ingredient" style={{ flex: 1 }} />
            <button type="submit" style={{ padding: '8px 12px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Add</button>
          </form>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
            {disliked.map((tag, idx) => (
              <span key={idx} style={{ padding: '6px 10px', borderRadius: 999, border: '2px solid var(--color-gray-200)', background: 'transparent' }}>
                {tag}
                <button onClick={() => removeTag(idx)} style={{ marginLeft: 8, border: 'none', background: 'transparent', cursor: 'pointer', color: '#ef4444' }}>×</button>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <button disabled={saving} onClick={save} style={{ padding: '10px 16px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: saving ? 'not-allowed' : 'pointer' }}>
          {saving ? 'Saving...' : 'Save Goals'}
        </button>
      </div>
    </div>
  );
}


