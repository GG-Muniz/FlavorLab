import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { absoluteUrl } from '../api/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export default function IngredientDetailPage() {
  const { ingredientId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [ingredient, setIngredient] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [grams, setGrams] = useState(100);
  const [allIds, setAllIds] = useState([]);

  // Attribute helpers and serving size (must be declared before effects that depend on them)
  const attrs = ingredient?.attributes || {};
  const unwrap = (v) => (v && typeof v === 'object' && 'value' in v ? v.value : v);
  const servingSizeG = unwrap(attrs?.serving_size_g);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setIsLoading(true);
        setError(null);
        const resp = await fetch(`${API_BASE_URL}/entities/${encodeURIComponent(ingredientId)}`);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.detail || 'Failed to load ingredient');
        if (mounted) setIngredient(data);
      } catch (e) {
        if (mounted) setError(e?.message || 'Failed to load ingredient');
      } finally {
        if (mounted) setIsLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [ingredientId]);

  // Fetch the overall ordering list (respects current filters by appending current query params)
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const query = location.search ? `${location.search}&` : '';
        // fetch large list to compute neighbors; keep stable ordering by name
        const resp = await fetch(`${API_BASE_URL}/entities/ingredients?${query}page=1&size=1000&sort=name_asc`);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.detail || 'Failed to load ordering');
        const ids = (Array.isArray(data) ? data : (data?.entities || [])).map(i => i.id);
        if (mounted) setAllIds(ids);
      } catch {}
    })();
    return () => { mounted = false; };
  }, [location.search]);

  const idx = useMemo(() => allIds.findIndex(id => id === ingredientId), [allIds, ingredientId]);
  const prevId = idx > 0 ? allIds[idx - 1] : null;
  const nextId = idx >= 0 && idx < allIds.length - 1 ? allIds[idx + 1] : null;

  // Default grams to serving size if present
  useEffect(() => {
    try {
      const val = servingSizeG;
      const n = typeof val === 'string' ? parseFloat(val) : (typeof val === 'number' ? val : NaN);
      if (Number.isFinite(n) && n > 0) {
        setGrams(n);
      }
    } catch {}
  }, [servingSizeG]);

  const cals = unwrap(attrs?.calories);
  const protein = unwrap(attrs?.protein_g);
  const carbs = unwrap(attrs?.carbs_g);
  const fat = unwrap(attrs?.fat_g);
  const fiber = unwrap(attrs?.fiber_g);
  const sugars = unwrap(attrs?.sugars_g);

  const toNum = (v) => {
    const n = typeof v === 'string' ? parseFloat(v) : (typeof v === 'number' ? v : NaN);
    return Number.isFinite(n) ? n : 0;
  };
  const gramsNum = Math.max(0, toNum(grams));
  const scale = gramsNum / 100 || 0;
  const fmt = (n, digits = 1) => {
    const base = toNum(n);
    const x = base * scale;
    return digits === 0 ? Math.round(x) : parseFloat(x.toFixed(digits));
  };

  const rawAttrImage = unwrap(attrs?.image_url);
  const rawImage = ingredient?.image_url || rawAttrImage;
  const imgSrc = rawImage ? absoluteUrl(rawImage) : null;
  const keyCompounds = unwrap(attrs?.key_compounds);
  const nutrientRefs = unwrap(attrs?.nutrient_references);
  const servingSizeSource = unwrap(attrs?.serving_size_g_source);

  const displayName = ingredient?.display_name || ingredient?.name;
  const list = (v) => Array.isArray(v) ? v : (v != null ? [v] : []);
  const fmtNutrientName = (n) => {
    if (n && typeof n === 'object') return n.nutrient_name || n.name || String(n);
    return String(n);
  };

  // Mini glossaries for brief benefits
  const compoundBenefit = (name) => {
    const key = String(name || '').toLowerCase();
    const map = {
      'allicin': 'antimicrobial; may support heart health',
      'quercetin': 'antioxidant; anti-inflammatory support',
      'catechins': 'antioxidant; metabolic and heart support',
      'curcumin': 'anti-inflammatory support',
      'gingerol': 'anti-inflammatory; digestive support',
      'shogaol': 'anti-nausea; anti-inflammatory support',
      'omega-3': 'brain and heart support',
      'melatonin': 'sleep regulation',
      'pectin': 'soluble fiber; may support cholesterol and gut health',
    };
    return map[key] || 'beneficial compound';
  };

  const vitaminMineralBenefit = (name) => {
    const key = String(name || '').toLowerCase();
    const map = {
      'vitamin c': 'immune support and antioxidant',
      'vitamin e': 'antioxidant; skin and cell protection',
      'vitamin b2': 'energy metabolism (riboflavin)',
      'vitamin b12': 'red blood cells and nerve health',
      'vitamin d': 'bone and immune support',
      'magnesium': 'muscle, nerve, and energy support',
      'iron': 'oxygen transport and energy',
      'zinc': 'immune function and wound healing',
      'selenium': 'antioxidant enzyme support',
      'potassium': 'fluid balance and heart function',
      'calcium': 'bone and muscle function',
    };
    return map[key] || 'supports overall wellness';
  };
  const fmtNutrientRef = (n) => {
    if (n && typeof n === 'object') {
      const name = n.nutrient_name || n.name || n.id || 'Nutrient';
      const conc = n.concentration != null && String(n.concentration).trim() !== '' ? ` — ${n.concentration}` : '';
      return `${name}${conc}`;
    }
    return String(n);
  };

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
      {/* Navigation row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => navigate(-1)} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }}>Back</button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button disabled={!prevId} onClick={() => prevId && navigate({ pathname: `/ingredients/${prevId}`, search: location.search })} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8, opacity: prevId ? 1 : 0.5 }}>Previous</button>
          <button disabled={!nextId} onClick={() => nextId && navigate({ pathname: `/ingredients/${nextId}`, search: location.search })} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8, opacity: nextId ? 1 : 0.5 }}>Next</button>
        </div>
      </div>
      {isLoading && <div>Loading...</div>}
      {error && <div style={{ color: '#b91c1c' }}>{error}</div>}
      {(!isLoading && !error && ingredient) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 96, height: 96, borderRadius: 16, overflow: 'hidden', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {imgSrc ? (
                <img src={imgSrc} alt={displayName} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <div style={{ fontSize: 36, fontWeight: 800, color: '#9ca3af' }}>{displayName?.charAt(0) || '?'}</div>
              )}
            </div>
            <h2 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: 'var(--color-gray-900)' }}>{displayName}</h2>
          </div>

          {/* Nutritional Information */}
          <div style={{ background: '#fff', border: '1px solid var(--color-gray-200)', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ marginTop: 0, marginBottom: 12, fontWeight: 800 }}>Nutritional Information (per {gramsNum}g)</h3>
              <div>
                <label style={{ fontSize: 12, color: 'var(--text-secondary)', marginRight: 8 }}>Grams:</label>
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={grams}
                  onChange={(e) => setGrams(e.target.value)}
                  style={{ width: 90, padding: '6px 8px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }}
                />
              </div>
            </div>
            {!!toNum(servingSizeG) && (
              <div style={{ marginBottom: 8, color: 'var(--text-secondary)' }}>
                Serving size: {toNum(servingSizeG)}g
              </div>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', rowGap: 8 }}>
              <div>Calories</div>
              <div style={{ textAlign: 'right' }}>{fmt(cals, 0)}</div>
              <div>Protein</div>
              <div style={{ textAlign: 'right' }}>{fmt(protein)}g</div>
              <div>Carbohydrates</div>
              <div style={{ textAlign: 'right' }}>{fmt(carbs)}g</div>
              <div>Fat</div>
              <div style={{ textAlign: 'right' }}>{fmt(fat)}g</div>
              {fiber != null && (
                <>
                  <div>Fiber</div>
                  <div style={{ textAlign: 'right' }}>{fmt(fiber)}g</div>
                </>
              )}
              {sugars != null && (
                <>
                  <div>Sugars</div>
                  <div style={{ textAlign: 'right' }}>{fmt(sugars)}g</div>
                </>
              )}
            </div>
          </div>

          {/* Composition */}
          <div style={{ background: '#fff', border: '1px solid var(--color-gray-200)', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'grid', gap: 12 }}>
              <div>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>Key Compounds</div>
                <ul style={{ margin: 0, paddingLeft: 18, listStyle: 'disc' }}>
                  {list(keyCompounds).map((c, idx) => (
                    <li key={idx}>
                      <span style={{ fontWeight: 600 }}>{String(c)}</span>
                      <span style={{ color: 'var(--text-secondary)' }}> — {compoundBenefit(String(c))}</span>
                    </li>
                  ))}
                </ul>
              </div>
              {!!list(nutrientRefs).length && (
                <div>
                  <div style={{ fontWeight: 700, marginBottom: 6 }}>Vitamins & Minerals</div>
                  <ul style={{ margin: 0, paddingLeft: 18, listStyle: 'disc' }}>
                    {list(nutrientRefs)
                      .map((n) => fmtNutrientName(n))
                      .filter((name) => name && !/^(protein|proteins|fat|fats)$/i.test(String(name)))
                      .filter((name, idx, arr) => arr.findIndex((x) => String(x).toLowerCase() === String(name).toLowerCase()) === idx)
                      .map((name, idx) => (
                        <li key={idx}>
                          <span style={{ fontWeight: 600 }}>{name}</span>
                          <span style={{ color: 'var(--text-secondary)' }}> — {vitaminMineralBenefit(name)}</span>
                        </li>
                      ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


