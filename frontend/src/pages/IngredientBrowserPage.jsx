import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { absoluteUrl } from '../api/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

function useDebouncedValue(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

const DEFAULT_CATEGORY_SLUGS = [
  'fruits','berries','vegetables','legumes','meats','seafood','nuts','seeds','grains'
];

export default function IngredientBrowserPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [ingredients, setIngredients] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const size = 24;

  const [selectedCategories, setSelectedCategories] = useState([]);
  const [minCalories, setMinCalories] = useState('');
  const [maxCalories, setMaxCalories] = useState('');
  const [minProtein, setMinProtein] = useState('');
  const [maxProtein, setMaxProtein] = useState('');

  const debouncedQuery = useDebouncedValue(searchQuery, 400);
  const initialized = useRef(false);

  // Initialize state from URL once
  useEffect(() => {
    if (initialized.current) return;
    const params = new URLSearchParams(location.search || '');
    const q = params.get('search') || '';
    const cats = (params.get('categories') || '').split(',').filter(Boolean);
    const p = parseInt(params.get('page') || '1', 10);
    const minCal = params.get('min_calories') || '';
    const maxCal = params.get('max_calories') || '';
    const minP = params.get('min_protein_g') || '';
    const maxP = params.get('max_protein_g') || '';
    if (q) setSearchQuery(q);
    if (cats.length) setSelectedCategories(cats.slice(0, 3));
    if (!Number.isNaN(p) && p > 0) setPage(p);
    if (minCal !== '') setMinCalories(minCal);
    if (maxCal !== '') setMaxCalories(maxCal);
    if (minP !== '') setMinProtein(minP);
    if (maxP !== '') setMaxProtein(maxP);
    initialized.current = true;
  }, [location.search]);

  async function fetchIngredients(p = 1) {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(p), size: String(size), sort: 'name_asc' });
      if (debouncedQuery && debouncedQuery.trim()) params.set('search', debouncedQuery.trim());
      if (selectedCategories.length) params.set('categories', selectedCategories.join(','));
      if (minCalories !== '') params.set('min_calories', String(minCalories));
      if (maxCalories !== '') params.set('max_calories', String(maxCalories));
      if (minProtein !== '') params.set('min_protein_g', String(minProtein));
      if (maxProtein !== '') params.set('max_protein_g', String(maxProtein));

      const resp = await fetch(`${API_BASE_URL}/entities/ingredients?${params.toString()}`);
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || 'Failed to load ingredients');
      setIngredients(Array.isArray(data) ? data : (data?.entities || []));
    } catch (e) {
      setError(e?.message || 'Failed to load ingredients');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchIngredients(page).catch(() => {});
  }, [page, debouncedQuery, selectedCategories.join(','), minCalories, maxCalories, minProtein, maxProtein]);

  // Persist state to URL
  useEffect(() => {
    const params = new URLSearchParams();
    if (debouncedQuery && debouncedQuery.trim()) params.set('search', debouncedQuery.trim());
    if (selectedCategories.length) params.set('categories', selectedCategories.join(','));
    if (minCalories !== '') params.set('min_calories', String(minCalories));
    if (maxCalories !== '') params.set('max_calories', String(maxCalories));
    if (minProtein !== '') params.set('min_protein_g', String(minProtein));
    if (maxProtein !== '') params.set('max_protein_g', String(maxProtein));
    if (page > 1) params.set('page', String(page));
    navigate({ pathname: location.pathname, search: params.toString() }, { replace: true });
  }, [page, debouncedQuery, selectedCategories.join(','), minCalories, maxCalories, minProtein, maxProtein]);

  const onPrev = () => setPage(p => Math.max(1, p - 1));
  const onNext = () => setPage(p => p + 1);

  const toggleCategory = (slug) => {
    setPage(1);
    setSelectedCategories((prev) => {
      const exists = prev.includes(slug);
      if (exists) return prev.filter(s => s !== slug);
      // cap at 3 chips
      if (prev.length >= 3) return [...prev.slice(1), slug];
      return [...prev, slug];
    });
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setMinCalories(''); setMaxCalories(''); setMinProtein(''); setMaxProtein('');
    setPage(1);
  };

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '24px 16px 16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 0 }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 800, color: 'var(--color-gray-900)' }}>Ingredient Library</h2>
        <div>
          <input
            value={searchQuery}
            onChange={e => { setSearchQuery(e.target.value); setPage(1); }}
            placeholder="Search ingredients..."
            style={{ padding: '10px 12px', borderRadius: 10, border: '1px solid var(--color-gray-300)', minWidth: 280 }}
          />
        </div>
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 0, marginBottom: 12 }}>Note: Card calories are per 100g. Nutrition data sourced from USDA FoodData Central (fdc.nal.usda.gov).</div>

      {/* Filters */}
      <div style={{ display: 'grid', gap: 12, marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {DEFAULT_CATEGORY_SLUGS.map(slug => {
            const active = selectedCategories.includes(slug);
            const label = slug.charAt(0).toUpperCase() + slug.slice(1);
            return (
              <button
                key={slug}
                onClick={() => toggleCategory(slug)}
                style={{
                  padding: '6px 10px', borderRadius: 9999, border: '1px solid var(--color-gray-300)',
                  background: active ? '#22c55e' : 'white', color: active ? '#fff' : 'var(--text-primary)', cursor: 'pointer'
                }}
              >{label}</button>
            );
          })}
          <button onClick={clearFilters} style={{ padding: '6px 10px', borderRadius: 9999, border: '1px solid var(--color-gray-300)', background: 'white', cursor: 'pointer' }}>Clear</button>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <label>Min Calories <input type="number" value={minCalories} onChange={(e)=>{setMinCalories(e.target.value); setPage(1);}} style={{ width: 90, padding: '6px 8px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }} /></label>
          <label>Max Calories <input type="number" value={maxCalories} onChange={(e)=>{setMaxCalories(e.target.value); setPage(1);}} style={{ width: 90, padding: '6px 8px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }} /></label>
          <label>Min Protein (g) <input type="number" value={minProtein} onChange={(e)=>{setMinProtein(e.target.value); setPage(1);}} style={{ width: 90, padding: '6px 8px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }} /></label>
          <label>Max Protein (g) <input type="number" value={maxProtein} onChange={(e)=>{setMaxProtein(e.target.value); setPage(1);}} style={{ width: 90, padding: '6px 8px', border: '1px solid var(--color-gray-300)', borderRadius: 8 }} /></label>
        </div>
        
      </div>

      {error && (
        <div style={{ color: '#b91c1c', marginBottom: 12 }}>{error}</div>
      )}

      {isLoading ? (
        <div style={{ padding: 24 }}>Loading...</div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: 16
        }}>
          {ingredients.map(ing => (
            <IngredientCard key={ing.id} ingredient={ing} />
          ))}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginTop: 20 }}>
        <button onClick={onPrev} disabled={page === 1} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid var(--color-gray-300)' }}>Previous</button>
        <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Page {page}</span>
        <button onClick={onNext} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid var(--color-gray-300)' }}>Next</button>
      </div>
    </div>
  );
}

function IngredientCard({ ingredient }) {
  const location = useLocation();
  const attrs = ingredient?.attributes || {};
  const name = ingredient?.display_name || ingredient?.name || 'Unknown';
  const cals = typeof attrs?.calories === 'object' ? attrs?.calories?.value : attrs?.calories;
  // Prefer top-level image_url, fallback to attribute location for backward compat
  const rawAttrImage = typeof attrs?.image_url === 'object' ? attrs?.image_url?.value : attrs?.image_url;
  const rawImage = ingredient?.image_url || rawAttrImage;
  const imgSrc = rawImage ? absoluteUrl(rawImage) : null;
  const unsplash = `https://source.unsplash.com/featured/?${encodeURIComponent((name || '').toLowerCase().replace(/\s+/g, ','))}`;
  const fallback = 'https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,c_fill,w_640,h_360/sample.jpg';

  return (
    <Link to={{ pathname: `/app/ingredients/${ingredient.id}`, search: location.search }} style={{
      display: 'block',
      textDecoration: 'none',
      border: '1px solid var(--color-gray-200)',
      borderRadius: 12,
      padding: 12,
      background: '#fff'
    }}>
      <div style={{ height: 120, borderRadius: 8, overflow: 'hidden', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
        <img
          src={imgSrc || unsplash}
          alt={name}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          onError={(e) => {
            if (e.currentTarget.src !== unsplash) { e.currentTarget.src = unsplash; return; }
            if (e.currentTarget.src !== fallback) e.currentTarget.src = fallback;
          }}
        />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ fontWeight: 700, color: 'var(--color-gray-900)' }}>{name}</div>
        {cals != null && (
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{cals} kcal</div>
        )}
      </div>
    </Link>
  );
}


