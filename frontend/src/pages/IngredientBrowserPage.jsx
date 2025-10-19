import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
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

export default function IngredientBrowserPage() {
  const [ingredients, setIngredients] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const size = 24;

  const debouncedQuery = useDebouncedValue(searchQuery, 400);

  async function fetchIngredients(p = 1) {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE_URL}/entities?classification=ingredient&page=${p}&size=${size}`);
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || 'Failed to load ingredients');
      setIngredients(data?.entities || []);
    } catch (e) {
      setError(e?.message || 'Failed to load ingredients');
    } finally {
      setIsLoading(false);
    }
  }

  async function searchIngredientsApi(query) {
    if (!query) { await fetchIngredients(1); return; }
    setIsLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE_URL}/entities/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, primary_classification: 'ingredient', limit: size, offset: 0 })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || 'Failed to search ingredients');
      setIngredients(data?.entities || []);
    } catch (e) {
      setError(e?.message || 'Failed to search ingredients');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchIngredients(page).catch(() => {});
  }, [page]);

  useEffect(() => {
    searchIngredientsApi(debouncedQuery).catch(() => {});
  }, [debouncedQuery]);

  const onPrev = () => setPage(p => Math.max(1, p - 1));
  const onNext = () => setPage(p => p + 1);

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 16 }}>
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
  const name = ingredient?.name || 'Unknown';
  const attrs = ingredient?.attributes || {};
  const cals = typeof attrs?.calories === 'object' ? attrs?.calories?.value : attrs?.calories;
  const imageUrl = typeof attrs?.image_url === 'object' ? attrs?.image_url?.value : attrs?.image_url;
  const imgSrc = imageUrl ? absoluteUrl(imageUrl) : null;

  return (
    <Link to={`/ingredients/${ingredient.id}`} style={{
      display: 'block',
      textDecoration: 'none',
      border: '1px solid var(--color-gray-200)',
      borderRadius: 12,
      padding: 12,
      background: '#fff'
    }}>
      <div style={{ height: 120, borderRadius: 8, overflow: 'hidden', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
        {imgSrc ? (
          <img src={imgSrc} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{ fontSize: 32, fontWeight: 700, color: '#9ca3af' }}>{name?.charAt(0) || '?'}</div>
        )}
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


