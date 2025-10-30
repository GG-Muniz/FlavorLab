import { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { getHealthPillars } from '../../services/healthPillarsApi';

const DIET_OPTIONS = [
  { value: '', label: 'Select' },
  { value: 'balanced', label: 'Balanced' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'keto', label: 'Keto' },
  { value: 'paleo', label: 'Paleo' },
  { value: 'pescatarian', label: 'Pescatarian' },
  { value: 'mediterranean', label: 'Mediterranean' }
];
const ALLERGENS = ['Dairy', 'Gluten', 'Peanuts', 'Tree Nuts', 'Soy', 'Eggs', 'Shellfish', 'Fish', 'Sesame'];

export default function GoalsPreferencesForm({ onSaved }) {
  const { user, updateProfile } = useAuth();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const initialPrefs = user?.preferences || user?.dietary_preferences || {};
  const initialGoalsRaw = user?.health_goals || initialPrefs?.health_goals || {};

  const [pillars, setPillars] = useState([]);
  const [selectedPillars, setSelectedPillars] = useState(() => {
    if (Array.isArray(initialGoalsRaw)) return initialGoalsRaw;
    if (Array.isArray(initialGoalsRaw?.selectedGoals)) return initialGoalsRaw.selectedGoals;
    return [];
  });

  const [diet, setDiet] = useState(initialPrefs?.diet || '');
  const [allergies, setAllergies] = useState(new Set(initialPrefs?.allergies || []));
  const [disliked, setDisliked] = useState(initialPrefs?.disliked || []);
  const [tagInput, setTagInput] = useState('');
  const [mealsPerDay, setMealsPerDay] = useState(initialPrefs?.meals_per_day || '');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  useEffect(() => {
    const q = (tagInput || '').trim();
    if (!q) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    const id = setTimeout(async () => {
      try {
        setIsSearching(true);
        setSearchError('');
        const resp = await fetch((import.meta.env.VITE_API_BASE_URL || '/api/v1') + '/entities/simple-search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name_contains: q })
        });
        const data = await resp.json();
        setSuggestions(Array.isArray(data?.results) ? data.results : []);
        setShowSuggestions(true);
      } catch (e) {
        setSearchError('Search failed');
        setSuggestions([]);
      } finally {
        setIsSearching(false);
      }
    }, 250);
    return () => clearTimeout(id);
  }, [tagInput]);

  useEffect(() => {
    const nextInitialGoals = user?.health_goals || {};
    const nextInitialPrefs = user?.preferences || user?.dietary_preferences || {};
    const nextSelected = Array.isArray(nextInitialGoals?.selectedGoals)
      ? nextInitialGoals.selectedGoals
      : (Array.isArray(nextInitialGoals) ? nextInitialGoals : []);
    setSelectedPillars(nextSelected);
    setDiet(nextInitialPrefs?.diet || '');
    setAllergies(new Set(nextInitialPrefs?.allergies || []));
    setDisliked(nextInitialPrefs?.disliked || []);
    setMealsPerDay(nextInitialPrefs?.meals_per_day || '');
  }, [user]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await getHealthPillars();
        if (!mounted) return;
        setPillars(data || []);
      } catch (e) {
        // ignore
      }
    })();
    return () => { mounted = false; };
  }, []);

  const toggleAllergy = (item) => {
    const next = new Set(allergies);
    if (next.has(item)) next.delete(item); else next.add(item);
    setAllergies(next);
  };

  const addTag = (e) => {
    e?.preventDefault();
    const val = (tagInput || '').trim();
    if (!val) return;
    if (!disliked.find(t => (t?.name || t) === val)) setDisliked([...disliked, { name: val }]);
    setTagInput('');
    setShowSuggestions(false);
  };

  const removeTag = (idx) => {
    const next = [...disliked];
    next.splice(idx, 1);
    setDisliked(next);
  };

  const selectSuggestion = (item) => {
    if (!item) return;
    const exists = disliked.find(t => (t?.id || t?.name) === item.id || t?.name === item.name);
    if (!exists) setDisliked([...disliked, { id: item.id, name: item.name }]);
    setTagInput('');
    setShowSuggestions(false);
  };

  const save = async () => {
    setSaving(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        health_goals: { selectedGoals: selectedPillars },
        dietary_preferences: {
          diet,
          allergies: Array.from(allergies),
          disliked: disliked.map(t => (typeof t === 'string' ? { name: t } : t)),
          meals_per_day: mealsPerDay || undefined
        }
      };
      await updateProfile(payload);
      setMessage('Goals & preferences saved');
      onSaved && onSaved();
    } catch (err) {
      setError(err?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ border: '2px solid var(--color-gray-200)', borderRadius: 12, padding: 16, background: 'var(--color-gray-100)', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
      <h3 style={{ marginTop: 0 }}>Goals & Preferences</h3>
      {message && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#ecfdf5', color: '#065f46', border: '1px solid #a7f3d0', borderRadius: 8 }}>{message}</div>}
      {error && <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: 8 }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Health Goals</div>
          <div style={{ display: 'grid', gap: 8 }}>
            {pillars.map(p => (
              <label key={p.id} style={{ display: 'flex', alignItems: 'center', gap: 8, border: '2px solid var(--color-gray-200)', borderRadius: 10, padding: '8px 10px', background: 'transparent' }}>
                <input
                  type="checkbox"
                  checked={selectedPillars.includes(p.id)}
                  onChange={(e) => {
                    const isChecked = e.target.checked;
                    setSelectedPillars(prev => {
                      if (isChecked) return prev.includes(p.id) ? prev : [...prev, p.id];
                      return prev.filter(id => id !== p.id);
                    });
                  }}
                />
                <div>
                  <div style={{ fontWeight: 600 }}>{p.name}</div>
                  {p.description && <div style={{ fontSize: 12, color: '#6b7280' }}>{p.description}</div>}
                </div>
              </label>
            ))}
          </div>
        </div>

        <div>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Dietary Preferences</div>
          <select value={diet} onChange={(e) => setDiet(e.target.value)} style={{ width: '100%', padding: '8px 10px', borderRadius: 10, border: '2px solid var(--color-gray-200)' }}>
            {DIET_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Allergies</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {ALLERGENS.map(item => (
                <button
                  key={item}
                  onClick={() => toggleAllergy(item)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 999,
                    border: allergies.has(item) ? '1px solid #22c55e' : '1px solid #e5e7eb',
                    background: allergies.has(item) ? '#f0fdf4' : '#ffffff',
                    color: allergies.has(item) ? '#16a34a' : '#4b5563',
                    cursor: 'pointer'
                  }}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Disliked Ingredients</div>
            <form onSubmit={addTag} style={{ display: 'flex', gap: 8 }}>
              <input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                placeholder="Add ingredient"
                style={{ flex: 1, padding: '8px 10px', borderRadius: 10, border: '2px solid #e5e7eb' }}
              />
              <button type="submit" style={{ padding: '8px 12px', borderRadius: 10, border: '1px solid #e5e7eb', background: '#fff' }}>Add</button>
            </form>
            {showSuggestions && (
              <div style={{ marginTop: 8, borderRadius: 12, border: '1px solid #e5e7eb', background: '#ffffff', maxHeight: 160, overflowY: 'auto' }}>
                {isSearching && <div style={{ padding: 12, color: '#6b7280' }}>Searching...</div>}
                {searchError && <div style={{ padding: 12, color: '#b91c1c' }}>{searchError}</div>}
                {!isSearching && !searchError && suggestions.length === 0 && <div style={{ padding: 12, color: '#6b7280' }}>No suggestions</div>}
                {suggestions.map(s => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => selectSuggestion(s)}
                    style={{
                      display: 'block',
                      width: '100%',
                      padding: '10px 12px',
                      textAlign: 'left',
                      border: 'none',
                      background: 'transparent',
                      cursor: 'pointer'
                    }}
                  >
                    {s.name}
                  </button>
                ))}
              </div>
            )}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
              {disliked.map((tag, idx) => (
                <div key={idx} style={{ display: 'inline-flex', gap: 6, alignItems: 'center', padding: '6px 10px', borderRadius: 999, background: '#f1f5f9', color: '#1f2937' }}>
                  <span>{tag?.name || tag}</span>
                  <button onClick={() => removeTag(idx)} style={{ border: 'none', background: 'transparent', color: '#ef4444', cursor: 'pointer' }}>×</button>
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Meals Per Day</div>
            <input
              value={mealsPerDay}
              onChange={(e) => setMealsPerDay(e.target.value)}
              placeholder="e.g. 3"
              style={{ width: '100%', padding: '8px 10px', borderRadius: 10, border: '2px solid #e5e7eb' }}
            />
          </div>
        </div>
      </div>

      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <button
          onClick={save}
          disabled={saving}
          style={{
            padding: '10px 18px',
            borderRadius: 10,
            border: 'none',
            background: saving ? '#e5e7eb' : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            color: '#ffffff',
            fontWeight: 600,
            cursor: saving ? 'not-allowed' : 'pointer'
          }}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
}
