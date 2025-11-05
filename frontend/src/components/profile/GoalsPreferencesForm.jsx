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

function normalizeDislikedList(items) {
  if (!Array.isArray(items)) return [];
  const normalizedList = [];
  items.forEach((item) => {
    if (typeof item === 'string') {
      const trimmed = item.trim();
      if (trimmed) normalizedList.push({ name: trimmed });
      return;
    }
    if (item && typeof item === 'object') {
      const normalized = { ...item };
      if (typeof normalized.name === 'string') normalized.name = normalized.name.trim();
      if (!normalized.name && typeof normalized.label === 'string') normalized.name = normalized.label.trim();
      if (!normalized.name && typeof normalized.value === 'string') normalized.name = normalized.value.trim();
      if (!normalized.name && normalized.id != null) normalized.name = String(normalized.id).trim();
      if (normalized.name) normalizedList.push(normalized);
      return;
    }
    const fallback = item ?? '';
    const fallbackName = typeof fallback === 'string' ? fallback.trim() : String(fallback).trim();
    if (fallbackName) normalizedList.push({ name: fallbackName });
  });
  return normalizedList;
}

function normalizeMealsValue(value) {
  if (typeof value !== 'string') return '';
  const trimmed = value.trim();
  if (trimmed === '3-meals') return '3';
  if (trimmed === '5-6-smaller' || trimmed === '5-6' || trimmed === '5-6-meals') return '6';
  if (trimmed === '3' || trimmed === '6' || trimmed === '3-meals-2-snacks') return trimmed;
  return trimmed;
}

function extractPreferenceState(user) {
  const prefs = user?.preferences || {};
  const dietaryPrefs = user?.dietary_preferences || prefs?.dietary_preferences || {};
  const surveyData = prefs?.survey_data || {};
  const dietFromSurvey = Array.isArray(surveyData?.dietaryRestrictions) ? (surveyData.dietaryRestrictions[0] || '') : '';
  const allergiesList = prefs?.allergies ?? dietaryPrefs?.allergies ?? surveyData?.allergies ?? [];
  const dislikedRaw = prefs?.disliked ?? dietaryPrefs?.disliked ?? surveyData?.dislikedIngredients ?? [];
  const mealsRaw = prefs?.meals_per_day ?? dietaryPrefs?.meals_per_day ?? surveyData?.mealsPerDay ?? '';
  const dietRaw = prefs?.diet ?? dietaryPrefs?.diet ?? dietFromSurvey ?? '';
  const dietNormalized = typeof dietRaw === 'string' ? dietRaw.trim().toLowerCase() : '';

  return {
    surveyData,
    diet: dietNormalized,
    allergies: Array.isArray(allergiesList)
      ? allergiesList
        .map((item) => (typeof item === 'string' ? item.trim() : item))
        .filter((item) => typeof item === 'string' && item.length > 0)
      : [],
    disliked: normalizeDislikedList(dislikedRaw),
    mealsPerDay: normalizeMealsValue(mealsRaw)
  };
}

export default function GoalsPreferencesForm({ onSaved }) {
  const { user, updateProfile } = useAuth();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const preferenceSnapshot = extractPreferenceState(user);
  const initialGoalsRaw = user?.health_goals || user?.preferences?.health_goals || {};

  // Health pillars list and selection (mirrors NutriTest)
  const [pillars, setPillars] = useState([]);
  const [selectedPillars, setSelectedPillars] = useState(() => {
    if (Array.isArray(initialGoalsRaw)) return initialGoalsRaw;
    if (Array.isArray(initialGoalsRaw?.selectedGoals)) return initialGoalsRaw.selectedGoals;
    return [];
  });

  const [diet, setDiet] = useState(preferenceSnapshot.diet || '');
  const [allergies, setAllergies] = useState(new Set(preferenceSnapshot.allergies || []));
  const [disliked, setDisliked] = useState(preferenceSnapshot.disliked || []);
  const [tagInput, setTagInput] = useState('');
  const [mealsPerDay, setMealsPerDay] = useState(preferenceSnapshot.mealsPerDay || '');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  // Debounced search for disliked ingredients
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

  // Sync local state with user changes from AuthContext
  useEffect(() => {
    const prefsState = extractPreferenceState(user);
    const nextInitialGoals = user?.health_goals || user?.preferences?.health_goals || {};
    const nextSelected = Array.isArray(nextInitialGoals?.selectedGoals)
      ? nextInitialGoals.selectedGoals
      : (Array.isArray(nextInitialGoals) ? nextInitialGoals : []);
    setSelectedPillars(nextSelected);
    setDiet(prefsState.diet || '');
    setAllergies(new Set(prefsState.allergies || []));
    setDisliked(prefsState.disliked || []);
    setMealsPerDay(prefsState.mealsPerDay || '');
  }, [user]);

  useEffect(() => {
    if (!Array.isArray(pillars) || pillars.length === 0) return;
    if (Array.isArray(selectedPillars) && selectedPillars.length > 0) return;
    const surveyNames = (user?.preferences?.survey_data?.healthPillars || []).filter(Boolean);
    if (!surveyNames.length) return;
    const mappedIds = surveyNames
      .map((name) => {
        const match = pillars.find((pillar) => (pillar?.name || pillar?.title) === name);
        return match?.id;
      })
      .filter(Boolean);
    if (mappedIds.length > 0) setSelectedPillars(mappedIds);
  }, [pillars, selectedPillars, user]);

  // Load pillars to mirror NutriTest labels
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await getHealthPillars();
        if (!mounted) return;
        setPillars(data || []);
      } catch (e) {
        // Non-fatal; leave empty list
      }
    })();
    return () => { mounted = false; };
  }, []);

  function toggleAllergy(item) {
    const next = new Set(allergies);
    if (next.has(item)) next.delete(item); else next.add(item);
    setAllergies(next);
  }

  function addTag(e) {
    e?.preventDefault();
    const val = (tagInput || '').trim();
    if (!val) return;
    // When free-typing, store as name-only tag
    if (!disliked.find(t => (t?.name || t) === val)) setDisliked([...disliked, { name: val }]);
    setTagInput('');
    setShowSuggestions(false);
  }

  function removeTag(idx) {
    const next = [...disliked];
    next.splice(idx, 1);
    setDisliked(next);
  }

  function selectSuggestion(item) {
    if (!item) return;
    const exists = disliked.find(t => (t?.id || t?.name) === item.id || t?.name === item.name);
    if (!exists) setDisliked([...disliked, { id: item.id, name: item.name }]);
    setTagInput('');
    setShowSuggestions(false);
  }

  async function save() {
    setSaving(true);
    setMessage('');
    setError('');
    try {
      const normalizedDiet = (diet || '').trim().toLowerCase();
      const normalizedAllergies = Array.from(allergies)
        .map((item) => (typeof item === 'string' ? item.trim() : item))
        .filter((item) => typeof item === 'string' && item.length > 0);
      const normalizedDisliked = normalizeDislikedList(disliked);
      const dislikedNames = normalizedDisliked
        .map((item) => (typeof item === 'string' ? item : item?.name))
        .filter(Boolean);

      const existingPreferences = user?.preferences || {};
      const existingSurvey = existingPreferences?.survey_data || {};
      const existingDietaryPrefs = user?.dietary_preferences || {};

      const computedPillarNames = pillars
        .filter((pillar) => selectedPillars.includes(pillar.id))
        .map((pillar) => pillar?.name || pillar?.title)
        .filter(Boolean);
      const fallbackSurveyPillars = Array.isArray(existingSurvey.healthPillars) ? existingSurvey.healthPillars : [];
      const surveyHealthPillars = computedPillarNames.length > 0 ? computedPillarNames : fallbackSurveyPillars;
      const nextPrimaryGoal = computedPillarNames.length > 0
        ? computedPillarNames[0]
        : (existingSurvey.primaryGoal || fallbackSurveyPillars[0] || undefined);

      const nextSurveyData = {
        ...existingSurvey,
        healthPillars: surveyHealthPillars,
        primaryGoal: nextPrimaryGoal,
        dietaryRestrictions: normalizedDiet ? [normalizedDiet] : [],
        allergies: normalizedAllergies,
        mealsPerDay: mealsPerDay || undefined,
        dislikedIngredients: dislikedNames
      };

      const sharedPreferences = {
        ...existingPreferences,
        health_goals: selectedPillars,
        allergies: normalizedAllergies,
        disliked: normalizedDisliked,
        meals_per_day: mealsPerDay || undefined,
        survey_data: nextSurveyData,
        ...(normalizedDiet ? { diet: normalizedDiet } : { diet: undefined })
      };

      const dietaryPreferencesPayload = {
        ...existingDietaryPrefs,
        allergies: normalizedAllergies,
        disliked: normalizedDisliked,
        meals_per_day: mealsPerDay || undefined,
        ...(normalizedDiet ? { diet: normalizedDiet } : { diet: undefined })
      };

      const payload = {
        // Write into both places for compatibility
        health_goals: { selectedGoals: selectedPillars },
        dietary_preferences: dietaryPreferencesPayload,
        preferences: sharedPreferences
      };
      console.log('GoalsPreferencesForm saving payload:', payload);
      console.log('Selected pillar IDs:', selectedPillars);
      console.log('Selected pillar names:', surveyHealthPillars);
      await updateProfile(payload);
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
                {p.name || p.title || `Goal ${p.id}`}
              </label>
            ))}
          </div>
        </div>

        <div>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Dietary Plan</div>
          <select value={diet} onChange={(e) => setDiet(e.target.value)} style={{ width: '100%' }}>
            {DIET_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
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

          <div style={{ fontWeight: 700, margin: '16px 0 8px 0' }}>Meals Per Day</div>
          <select value={mealsPerDay} onChange={(e) => setMealsPerDay(e.target.value)} style={{ width: '100%' }}>
            <option value="">Select</option>
            <option value="3">3 Meals</option>
            <option value="3-meals-2-snacks">3 Meals + 2 Snacks</option>
            <option value="6">5-6 Smaller Meals</option>
          </select>

          <div style={{ fontWeight: 700, margin: '16px 0 8px 0' }}>Disliked Ingredients</div>
          <div style={{ position: 'relative' }}>
            <form onSubmit={addTag} style={{ display: 'flex', gap: 8 }}>
              <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} placeholder="Search to add ingredient" style={{ flex: 1 }} />
              <button type="submit" style={{ padding: '8px 12px', borderRadius: 10, background: '#22c55e', color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Add</button>
            </form>
            {showSuggestions && (suggestions?.length > 0 || isSearching || searchError) && (
              <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, marginTop: 4, zIndex: 10 }}>
                {isSearching && <div style={{ padding: 8, color: '#6b7280' }}>Searching...</div>}
                {searchError && <div style={{ padding: 8, color: '#b91c1c' }}>{searchError}</div>}
                {suggestions.map(item => (
                  <button key={item.id} type="button" onClick={() => selectSuggestion(item)} style={{ width: '100%', textAlign: 'left', padding: 8, background: 'transparent', border: 'none', cursor: 'pointer' }}>
                    {item.name}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
            {disliked.map((tag, idx) => (
              <span key={idx} style={{ padding: '6px 10px', borderRadius: 999, border: '2px solid var(--color-gray-200)', background: 'transparent' }}>
                {tag?.name || tag}
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


