import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { absoluteUrl } from '../api/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const authHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
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

  const attrs = ingredient?.attributes || {};
  const unwrap = (value) => (value && typeof value === 'object' && 'value' in value ? value.value : value);
  const servingSizeG = unwrap(attrs?.serving_size_g);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setIsLoading(true);
      setError(null);
      try {
        const resp = await fetch(`${API_BASE_URL}/entities/ingredients/${ingredientId}`, {
          headers: authHeaders()
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.detail || 'Failed to load ingredient');
        if (mounted) setIngredient(data);
      } catch (err) {
        if (mounted) setError(err?.message || 'Failed to load ingredient');
      } finally {
        if (mounted) setIsLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [ingredientId]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const query = location.search ? `${location.search}&` : '';
        const resp = await fetch(`${API_BASE_URL}/entities/ingredients?${query}page=1&size=1000&sort=name_asc`, {
          headers: authHeaders()
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.detail || 'Failed to load ordering');
        const ids = (Array.isArray(data) ? data : (data?.entities || [])).map(i => i.id);
        if (mounted) setAllIds(ids);
      } catch (err) {
        console.error('Failed to load ingredient ordering:', err);
      }
    })();
    return () => { mounted = false; };
  }, [location.search]);

  const idx = useMemo(() => allIds.findIndex(id => id === ingredientId), [allIds, ingredientId]);
  const prevId = idx > 0 ? allIds[idx - 1] : null;
  const nextId = idx >= 0 && idx < allIds.length - 1 ? allIds[idx + 1] : null;

  useEffect(() => {
    if (servingSizeG && Number.isFinite(Number(servingSizeG))) {
      setGrams(Number(servingSizeG));
    }
  }, [servingSizeG]);

  const cals = unwrap(attrs?.calories);
  const protein = unwrap(attrs?.protein_g);
  const carbs = unwrap(attrs?.carbs_g);
  const fat = unwrap(attrs?.fat_g);
  const fiber = unwrap(attrs?.fiber_g);
  const sugars = unwrap(attrs?.sugars_g);

  const toNum = (value) => {
    const num = Number(value);
    return Number.isFinite(num) ? num : 0;
  };
  const gramsNum = Math.max(0, toNum(grams));
  const scale = gramsNum / 100 || 0;
  const fmt = (value, digits = 1) => (value == null ? '—' : Number.parseFloat(value).toFixed(digits));

  const rawAttrImage = unwrap(attrs?.image_url);
  const rawImage = ingredient?.image_url || rawAttrImage;
  const imgSrc = rawImage ? absoluteUrl(rawImage) : null;
  const keyCompounds = unwrap(attrs?.key_compounds);
  const nutrientRefs = unwrap(attrs?.nutrient_references);
  const servingSizeSource = unwrap(attrs?.serving_size_g_source);

  const displayName = ingredient?.display_name || ingredient?.name;
  const list = (value) => Array.isArray(value) ? value : (value != null ? [value] : []);
  const fmtLabel = (value) => {
    if (!value) return '';
    if (typeof value !== 'string') return String(value);
    return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const renderCompound = (item, idx) => {
    if (!item) return null;
    if (typeof item === 'string') {
      return <li key={`compound-${idx}`}>{fmtLabel(item)}</li>;
    }
    if (typeof item === 'object') {
      const compoundName = item.name || item.compound || item.title || '';
      const benefit = item.benefit || item.effect || item.description || '';
      if (!compoundName && !benefit) return null;
      return (
        <li key={`compound-${idx}`}>
          {compoundName ? <span style={{ fontWeight: 600 }}>{fmtLabel(compoundName)}</span> : null}
          {benefit ? <span>{compoundName ? ' — ' : ''}{benefit}</span> : null}
        </li>
      );
    }
    return null;
  };

  const renderNutrient = (item, idx) => {
    if (!item) return null;
    if (typeof item === 'string') {
      return <li key={`nutrient-${idx}`}>{fmtLabel(item)}</li>;
    }
    if (typeof item === 'object') {
      const name = item.nutrient || item.name || item.nutrient_name || item.id || '';
      const benefit = item.benefit || item.description || item.effect || '';
      const reference = item.reference || item.source || '';
      return (
        <li key={`nutrient-${idx}`}>
          {name ? <span style={{ fontWeight: 600 }}>{fmtLabel(name)}</span> : null}
          {benefit ? <span>{name ? ' — ' : ''}{benefit}</span> : null}
          {!benefit && reference ? <span>{name ? ' — ' : ''}{reference}</span> : null}
        </li>
      );
    }
    return null;
  };

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => navigate(-1)} style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }}>Back</button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            disabled={!prevId}
            onClick={() => prevId && navigate({ pathname: `/ingredients/${prevId}`, search: location.search })}
            style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8, opacity: prevId ? 1 : 0.5 }}
          >
            Previous
          </button>
          <button
            disabled={!nextId}
            onClick={() => nextId && navigate({ pathname: `/ingredients/${nextId}`, search: location.search })}
            style={{ padding: '8px 12px', border: '1px solid var(--color-gray-300)', borderRadius: 8, opacity: nextId ? 1 : 0.5 }}
          >
            Next
          </button>
        </div>
      </div>

      {isLoading && <div>Loading...</div>}
      {error && <div style={{ color: '#b91c1c' }}>{error}</div>}

      {(!isLoading && !error && ingredient) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(240px, 320px) 1fr', gap: 24 }}>
          <div>
            <div style={{ borderRadius: 16, overflow: 'hidden', background: '#f3f4f6', marginBottom: 16 }}>
              {imgSrc ? (
                <img src={imgSrc} alt={displayName} style={{ width: '100%', height: 240, objectFit: 'cover' }} />
              ) : (
                <div style={{ padding: '40px 0', textAlign: 'center', color: '#6b7280' }}>No image available</div>
              )}
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 700, color: '#111827', marginBottom: 8 }}>{displayName}</h1>
            {unwrap(attrs?.description) ? (
              <p style={{ color: '#6b7280', fontSize: 14, lineHeight: 1.6 }}>{unwrap(attrs?.description)}</p>
            ) : null}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ padding: 20, borderRadius: 16, border: '1px solid #e5e7eb', background: '#f9fafb' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontSize: 16, fontWeight: 600, color: '#111827' }}>Nutrition (per {gramsNum || 100}g)</span>
                <input
                  type="number"
                  value={grams}
                  onChange={(e) => setGrams(e.target.value)}
                  style={{ width: 90, padding: '8px 10px', borderRadius: 10, border: '1px solid #d1d5db' }}
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 8, fontSize: 14, color: '#374151' }}>
                <NutritionRow label="Calories" value={fmt((cals || 0) * scale, 0)} unit="kcal" />
                <NutritionRow label="Protein" value={fmt((protein || 0) * scale)} unit="g" />
                <NutritionRow label="Carbs" value={fmt((carbs || 0) * scale)} unit="g" />
                <NutritionRow label="Fat" value={fmt((fat || 0) * scale)} unit="g" />
                <NutritionRow label="Fiber" value={fmt((fiber || 0) * scale)} unit="g" />
                <NutritionRow label="Sugars" value={fmt((sugars || 0) * scale)} unit="g" />
              </div>
              {servingSizeG && (
                <div style={{ marginTop: 12, fontSize: 12, color: '#6b7280' }}>
                  Serving size: {fmt(servingSizeG, 0)} g {servingSizeSource ? `(source: ${servingSizeSource})` : ''}
                </div>
              )}
            </div>

            {list(keyCompounds).length > 0 && (
              <div style={{ padding: 20, borderRadius: 16, border: '1px solid #e0e7ff', background: '#eef2ff' }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, color: '#3730a3', marginBottom: 10 }}>Key Compounds</h3>
                <ul style={{ margin: 0, paddingLeft: 18, color: '#4338ca', fontSize: 14 }}>
                  {list(keyCompounds).map((compound, idx) => renderCompound(compound, idx))}
                </ul>
              </div>
            )}

            {list(nutrientRefs).length > 0 && (
              <div style={{ padding: 20, borderRadius: 16, border: '1px solid #d1fae5', background: '#ecfdf5' }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, color: '#047857', marginBottom: 10 }}>Nutrient Highlights</h3>
                <ul style={{ margin: 0, paddingLeft: 18, color: '#059669', fontSize: 14 }}>
                  {list(nutrientRefs).map((ref, idx) => renderNutrient(ref, idx))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function NutritionRow({ label, value, unit }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 0' }}>
      <span>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}{unit}</span>
    </div>
  );
}


