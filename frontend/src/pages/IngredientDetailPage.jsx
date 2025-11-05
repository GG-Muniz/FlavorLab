import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { absoluteUrl } from '../api/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const COMPOUND_BENEFITS = [
  {
    match: ['monounsaturated', 'oleic'],
    description: 'Heart-healthy fats that support cholesterol balance and brain function.'
  },
  {
    match: ['polyunsaturated', 'omega-3', 'epa', 'dha'],
    description: 'Essential fats that help reduce inflammation and protect the heart and brain.'
  },
  {
    match: ['potassium'],
    description: 'Key electrolyte that keeps blood pressure balanced and supports nerve and muscle function.'
  },
  {
    match: ['magnesium'],
    description: 'Mineral that supports muscle relaxation, bone health, and energy production.'
  },
  {
    match: ['natural sugars', 'fructose', 'glucose', 'sucrose'],
    description: 'Naturally occurring sugars that provide quick energy along with fiber and micronutrients.'
  },
  {
    match: ['folate', 'folic'],
    description: 'B-vitamin essential for healthy blood cells, energy, and prenatal development.'
  },
  {
    match: ['catechin', 'egcg'],
    description: 'Powerful tea antioxidants that support metabolic health and fight oxidative stress.'
  },
  {
    match: ['curcumin'],
    description: 'Turmeric compound known for its anti-inflammatory and antioxidant benefits.'
  },
  {
    match: ['gingerol', 'shogaol'],
    description: 'Ginger actives that soothe digestion and may calm nausea and inflammation.'
  },
  {
    match: ['polyphenol', 'resveratrol', 'anthocyanin', 'tannin'],
    description: 'Plant antioxidants that defend against cell damage and support circulation.'
  }
];

const VITAMIN_MINERAL_BENEFITS = [
  {
    match: ['vitamin c', 'ascorbic'],
    description: 'Immune-supporting antioxidant that promotes collagen production and healing.'
  },
  {
    match: ['vitamin e'],
    description: 'Protective antioxidant that shields cells and supports healthy skin.'
  },
  {
    match: ['vitamin b6'],
    description: 'B-vitamin for metabolism, energy production, and healthy nervous system function.'
  },
  {
    match: ['vitamin b12'],
    description: 'Crucial for red blood cell formation, energy, and brain health.'
  },
  {
    match: ['vitamin d'],
    description: 'Supports immunity, bone strength, and mood balance.'
  },
  {
    match: ['fiber'],
    description: 'Supports digestion, gut health, and steady energy by slowing sugar absorption.'
  },
  {
    match: ['iron'],
    description: 'Carries oxygen in the blood and helps fight fatigue.'
  },
  {
    match: ['zinc'],
    description: 'Essential for immune function, wound healing, and metabolism.'
  },
  {
    match: ['calcium'],
    description: 'Important for strong bones, teeth, and proper muscle contraction.'
  },
  {
    match: ['selenium'],
    description: 'Antioxidant mineral that supports thyroid function and immunity.'
  }
];

const resolveBenefit = (name, table, fallback) => {
  const key = String(name || '').toLowerCase();
  const entry = table.find(item => item.match.some(m => key.includes(m)));
  return entry?.description || fallback;
};

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
  const servingSizeSource = unwrap(attrs?.serving_size_g_source);
  const primaryBenefits = unwrap(attrs?.primary_benefits);
  const compoundConcentrations = unwrap(attrs?.compound_concentrations) || {};

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

  const displayName = ingredient?.display_name || ingredient?.name;
  const list = (v) => Array.isArray(v) ? v : (v != null ? [v] : []);
  const fmtNutrientName = (n) => {
    if (n && typeof n === 'object') return n.nutrient_name || n.name || String(n);
    return String(n);
  };

  const renderCompoundBenefit = (name) => resolveBenefit(name, COMPOUND_BENEFITS, 'Beneficial compound that supports overall wellness.');
  const renderNutrientBenefit = (name) => resolveBenefit(name, VITAMIN_MINERAL_BENEFITS, 'Supports overall wellness.');

  const maybeConcentration = (name) => {
    const key = String(name || '').toLowerCase();
    const direct = compoundConcentrations[key];
    if (direct) return ` (${direct})`;
    // Try normalized key without spaces
    const norm = key.replace(/\s+/g, '-');
    if (compoundConcentrations[norm]) return ` (${compoundConcentrations[norm]})`;
    return '';
  };

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
      {/* Navigation row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => navigate(-1)} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }}>Back</button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button disabled={!prevId} onClick={() => prevId && navigate({ pathname: `/app/ingredients/${prevId}`, search: location.search })} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8, opacity: prevId ? 1 : 0.5 }}>Previous</button>
          <button disabled={!nextId} onClick={() => nextId && navigate({ pathname: `/app/ingredients/${nextId}`, search: location.search })} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8, opacity: nextId ? 1 : 0.5 }}>Next</button>
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
            <div>
              <h2 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: 'var(--color-gray-900)' }}>{displayName}</h2>
              {!!list(primaryBenefits).length && (
                <div style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
                  {list(primaryBenefits).join(' • ')}
                </div>
              )}
            </div>
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
              <div style={{ marginBottom: 8, color: 'var(--text-secondary)', fontSize: 13 }}>
                Serving size reference: {toNum(servingSizeG)}g{servingSizeSource ? ` (${servingSizeSource})` : ''}
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
            <div style={{ display: 'grid', gap: 16 }}>
              <div>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>Key Compounds</div>
                <ul style={{ margin: 0, paddingLeft: 18, listStyle: 'disc' }}>
                  {list(keyCompounds).map((c, idx) => (
                    <li key={idx}>
                      <span style={{ fontWeight: 600 }}>{String(c)}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>{maybeConcentration(c)}</span>
                      <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{renderCompoundBenefit(String(c))}</div>
                    </li>
                  ))}
                </ul>
              </div>
              {!!list(nutrientRefs).length && (
                <div>
                  <div style={{ fontWeight: 700, marginBottom: 6 }}>Vitamins & Minerals</div>
                  <ul style={{ margin: 0, paddingLeft: 18, listStyle: 'disc' }}>
                    {list(nutrientRefs)
                      .map((n) => ({
                        name: fmtNutrientName(n),
                        concentration: n?.concentration
                      }))
                      .filter(({ name }) => name && !/^(protein|proteins|fat|fats)$/i.test(String(name)))
                      .filter((item, idx, arr) => arr.findIndex(x => String(x.name).toLowerCase() === String(item.name).toLowerCase()) === idx)
                      .map((item, idx) => (
                        <li key={idx}>
                          <span style={{ fontWeight: 600 }}>{item.name}</span>
                          {item.concentration ? <span style={{ color: 'var(--text-secondary)' }}> ({item.concentration})</span> : null}
                          <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{renderNutrientBenefit(item.name)}</div>
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


