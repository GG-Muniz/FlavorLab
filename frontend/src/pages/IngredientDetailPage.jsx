import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export default function IngredientDetailPage() {
  const { ingredientId } = useParams();
  const [ingredient, setIngredient] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const attrs = ingredient?.attributes || {};
  const cals = typeof attrs?.calories === 'object' ? attrs?.calories?.value : attrs?.calories;
  const protein = typeof attrs?.protein_g === 'object' ? attrs?.protein_g?.value : attrs?.protein_g;
  const carbs = typeof attrs?.carbs_g === 'object' ? attrs?.carbs_g?.value : attrs?.carbs_g;
  const fat = typeof attrs?.fat_g === 'object' ? attrs?.fat_g?.value : attrs?.fat_g;
  const imageUrl = typeof attrs?.image_url === 'object' ? attrs?.image_url?.value : attrs?.image_url;
  const keyCompounds = typeof attrs?.key_compounds === 'object' ? attrs?.key_compounds?.value : attrs?.key_compounds;
  const nutrientRefs = typeof attrs?.nutrient_references === 'object' ? attrs?.nutrient_references?.value : attrs?.nutrient_references;

  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
      {isLoading && <div>Loading...</div>}
      {error && <div style={{ color: '#b91c1c' }}>{error}</div>}
      {(!isLoading && !error && ingredient) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 96, height: 96, borderRadius: 16, overflow: 'hidden', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {imageUrl ? (
                <img src={imageUrl} alt={ingredient.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <div style={{ fontSize: 36, fontWeight: 800, color: '#9ca3af' }}>{ingredient.name?.charAt(0) || '?'}</div>
              )}
            </div>
            <h2 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: 'var(--color-gray-900)' }}>{ingredient.name}</h2>
          </div>

          {/* Nutritional Information */}
          <div style={{ background: '#fff', border: '1px solid var(--color-gray-200)', borderRadius: 12, padding: 16 }}>
            <h3 style={{ marginTop: 0 }}>Nutritional Information (per 100g)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', rowGap: 8 }}>
              <div>Calories</div>
              <div style={{ textAlign: 'right' }}>{cals ?? 0}</div>
              <div>Protein</div>
              <div style={{ textAlign: 'right' }}>{protein ?? 0} g</div>
              <div>Carbohydrates</div>
              <div style={{ textAlign: 'right' }}>{carbs ?? 0} g</div>
              <div>Fat</div>
              <div style={{ textAlign: 'right' }}>{fat ?? 0} g</div>
            </div>
          </div>

          {/* Composition */}
          <div style={{ background: '#fff', border: '1px solid var(--color-gray-200)', borderRadius: 12, padding: 16 }}>
            <h3 style={{ marginTop: 0 }}>Key Composition</h3>
            <div style={{ display: 'grid', gap: 12 }}>
              <div>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>Key Compounds</div>
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                  {(Array.isArray(keyCompounds) ? keyCompounds : (keyCompounds ? [keyCompounds] : [])).map((c, idx) => (
                    <li key={idx}>{String(c)}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>Nutrients</div>
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                  {(Array.isArray(nutrientRefs) ? nutrientRefs : (nutrientRefs ? [nutrientRefs] : [])).map((n, idx) => (
                    <li key={idx}>{String(n)}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


