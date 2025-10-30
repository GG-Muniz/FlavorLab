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
  'fruits', 'berries', 'vegetables', 'legumes', 'meats', 'seafood', 'nuts', 'seeds', 'grains'
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

  useEffect(() => {
    if (initialized.current) return;
    const params = new URLSearchParams(location.search);
    const search = params.get('search');
    const categories = params.get('categories');
    const minCal = params.get('min_calories');
    const maxCal = params.get('max_calories');
    const minProt = params.get('min_protein_g');
    const maxProt = params.get('max_protein_g');
    const pageParam = params.get('page');

    if (search) setSearchQuery(search);
    if (categories) setSelectedCategories(categories.split(',').filter(Boolean));
    if (minCal !== null) setMinCalories(minCal);
    if (maxCal !== null) setMaxCalories(maxCal);
    if (minProt !== null) setMinProtein(minProt);
    if (maxProt !== null) setMaxProtein(maxProt);
    if (pageParam) setPage(Number(pageParam));

    initialized.current = true;
  }, [location.search]);

  async function fetchIngredients(p = 1) {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.set('page', String(p));
      params.set('size', String(size));
      if (debouncedQuery && debouncedQuery.trim()) params.set('search', debouncedQuery.trim());
      if (selectedCategories.length) params.set('categories', selectedCategories.join(','));
      if (minCalories !== '') params.set('min_calories', String(minCalories));
      if (maxCalories !== '') params.set('max_calories', String(maxCalories));
      if (minProtein !== '') params.set('min_protein_g', String(minProtein));
      if (maxProtein !== '') params.set('max_protein_g', String(maxProtein));

      const response = await fetch(`${API_BASE_URL}/entities/ingredients?${params.toString()}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || 'Failed to fetch ingredients');
      setIngredients(Array.isArray(data?.entities) ? data.entities : data);
    } catch (err) {
      console.error('Ingredient fetch failed:', err);
      setError(err?.message || 'Failed to load ingredients');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchIngredients(page).catch(() => {});
  }, [page, debouncedQuery, selectedCategories.join(','), minCalories, maxCalories, minProtein, maxProtein]);

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
    setSelectedCategories(prev => prev.includes(slug) ? prev.filter(s => s !== slug) : [...prev, slug]);
    setPage(1);
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setMinCalories('');
    setMaxCalories('');
    setMinProtein('');
    setMaxProtein('');
    setPage(1);
  };

  const filteredIngredients = useMemo(() => ingredients, [ingredients]);

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '24px 16px 16px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 24 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          <input
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
            placeholder="Search ingredients..."
            style={{ flex: '1 1 260px', padding: '12px 14px', borderRadius: 12, border: '2px solid #e5e7eb' }}
          />
          <button
            onClick={clearFilters}
            style={{ padding: '12px 16px', borderRadius: 12, border: '1px solid #e5e7eb', background: '#fff' }}
          >
            Clear
          </button>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          {DEFAULT_CATEGORY_SLUGS.map(slug => (
            <button
              key={slug}
              onClick={() => toggleCategory(slug)}
              style={{
                padding: '10px 14px',
                borderRadius: 12,
                border: selectedCategories.includes(slug) ? '2px solid #22c55e' : '2px solid #e5e7eb',
                background: selectedCategories.includes(slug) ? '#f0fdf4' : '#ffffff',
                color: selectedCategories.includes(slug) ? '#16a34a' : '#374151',
                cursor: 'pointer'
              }}
            >
              {slug.replace(/-/g, ' ')}
            </button>
          ))}
        </div>

        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
          <FilterInput label="Min Calories" value={minCalories} setValue={setMinCalories} />
          <FilterInput label="Max Calories" value={maxCalories} setValue={setMaxCalories} />
          <FilterInput label="Min Protein (g)" value={minProtein} setValue={setMinProtein} />
          <FilterInput label="Max Protein (g)" value={maxProtein} setValue={setMaxProtein} />
        </div>
      </div>

      {error && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '12px 16px', borderRadius: 12, color: '#b91c1c', marginBottom: 16 }}>
          {error}
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: '16px'
        }}
      >
        {isLoading ? (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '32px 0' }}>Loading...</div>
        ) : (
          filteredIngredients.map(ingredient => (
            <IngredientCard key={ingredient.id} ingredient={ingredient} />
          ))
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
        <button
          onClick={onPrev}
          disabled={page === 1 || isLoading}
          style={{
            padding: '10px 16px',
            borderRadius: 10,
            border: '1px solid #e5e7eb',
            background: page === 1 ? '#f3f4f6' : '#ffffff',
            color: '#374151',
            cursor: page === 1 ? 'not-allowed' : 'pointer'
          }}
        >
          Previous
        </button>
        <div style={{ alignSelf: 'center', color: '#6b7280', fontWeight: 600 }}>Page {page}</div>
        <button
          onClick={onNext}
          disabled={isLoading || filteredIngredients.length < size}
          style={{
            padding: '10px 16px',
            borderRadius: 10,
            border: '1px solid #22c55e',
            background: '#22c55e',
            color: '#ffffff',
            cursor: isLoading || filteredIngredients.length < size ? 'not-allowed' : 'pointer',
            opacity: isLoading || filteredIngredients.length < size ? 0.6 : 1
          }}
        >
          Next
        </button>
      </div>
    </div>
  );
}

function FilterInput({ label, value, setValue }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>{label}</span>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder=""
        style={{ padding: '10px 12px', borderRadius: 10, border: '2px solid #e5e7eb' }}
      />
    </label>
  );
}

function IngredientCard({ ingredient }) {
  const location = useLocation();
  const attrs = ingredient?.attributes || {};
  const name = ingredient?.display_name || ingredient?.name || 'Unknown';
  const cals = typeof attrs?.calories === 'object' ? attrs?.calories?.value : attrs?.calories;
  const rawAttrImage = typeof attrs?.image_url === 'object' ? attrs?.image_url?.value : attrs?.image_url;
  const rawImage = ingredient?.image_url || rawAttrImage;
  const imgSrc = rawImage ? absoluteUrl(rawImage) : null;
  const unsplash = `https://source.unsplash.com/featured/?${encodeURIComponent((name || '').toLowerCase().replace(/\s+/g, ','))}`;
  const fallback = 'https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,c_fill,w_640,h_360/sample.jpg';

  return (
    <Link to={{ pathname: `/ingredients/${ingredient.id}`, search: location.search }} style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      padding: '16px',
      borderRadius: '16px',
      border: '1px solid #e5e7eb',
      background: '#ffffff',
      boxShadow: '0 1px 2px rgba(15, 23, 42, 0.08)',
      transition: 'all 0.2s',
      textDecoration: 'none'
    }}>
      <div style={{
        height: 120,
        borderRadius: 12,
        overflow: 'hidden',
        background: '#f3f4f6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
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
        <div style={{ fontWeight: 700, color: '#111827' }}>{name}</div>
        {cals != null && (
          <div style={{ fontSize: 12, color: '#6b7280' }}>{cals} kcal</div>
        )}
      </div>
    </Link>
  );
}


