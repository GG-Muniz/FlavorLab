import { useEffect, useMemo, useState } from 'react';
import { X, Search, Plus } from 'lucide-react';
import { searchIngredients } from '../../services/mealsApi';
import { useData } from '../../context/DataContext';

export default function LogMealModal({ isOpen, onClose, onSaved }) {
  const { refetchAll } = useData();
  const [mealType, setMealType] = useState('Breakfast');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState([]); // [{id, name, grams}]
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    setQuery(''); setResults([]); setSelected([]); setMealType('Breakfast'); setError(null);
  }, [isOpen]);

  useEffect(() => {
    let active = true;
    const run = async () => {
      if (!query.trim()) { setResults([]); return; }
      try {
        setLoading(true); setError(null);
        const ents = await searchIngredients(query, 8, 0);
        if (active) setResults(ents);
      } catch (e) {
        if (active) setError(e?.message || 'Search failed');
      } finally {
        if (active) setLoading(false);
      }
    };
    const t = setTimeout(run, 300);
    return () => { active = false; clearTimeout(t); };
  }, [query]);

  if (!isOpen) return null;

  const addIngredient = (ing) => {
    if (selected.some(s => s.id === ing.id)) return;
    setSelected([...selected, { id: ing.id, name: ing.name, grams: '' }]);
  };

  const updateGrams = (id, grams) => {
    setSelected(sel => sel.map(s => s.id === id ? { ...s, grams } : s));
  };

  const removeSelected = (id) => {
    setSelected(sel => sel.filter(s => s.id !== id));
  };

  const save = async () => {
    try {
      setLoading(true); setError(null);
      const today = new Date().toISOString().slice(0,10);
      const entries = selected
        .map(s => ({ ingredient_id: s.id, quantity_grams: Math.round(parseFloat(s.grams)) })) // CRITICAL FIX: Round to integer
        .filter(e => !Number.isNaN(e.quantity_grams) && e.quantity_grams > 0);
      if (entries.length === 0) { setError('Add at least one ingredient with grams'); setLoading(false); return; }

      // Use the meals API to log the meal
      const response = await fetch('/api/v1/meals/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ log_date: today, meal_type: mealType, entries })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.detail || 'Failed to log meal');
      }

      // The API now returns updated dashboard summary, no need for separate refetch
      // The response will be handled by the parent component's refetchAll
      await refetchAll();

      if (onSaved) onSaved();
      onClose();
    } catch (e) {
      setError(e?.message || 'Failed to save meal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div onClick={onClose} style={{ position:'fixed', inset:0, background:'rgba(0,0,0,0.4)', zIndex:1000 }} />
      <div style={{ position:'fixed', top:'50%', left:'50%', transform:'translate(-50%,-50%)', width:'90%', maxWidth:720, background:'#fff', borderRadius:16, border:'1px solid #e5e7eb', boxShadow:'0 25px 50px -12px rgba(0,0,0,0.25)', zIndex:1001 }}>
        <div style={{ padding:16, borderBottom:'1px solid #f3f4f6', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div style={{ fontSize:18, fontWeight:700 }}>Log Meal</div>
          <button onClick={onClose} style={{ border:'none', background:'transparent', cursor:'pointer' }}><X width={18} height={18} /></button>
        </div>
        <div style={{ padding:16, display:'grid', gap:16 }}>
          {error && <div style={{ color:'#b91c1c', border:'1px solid #fecaca', background:'#fef2f2', padding:8, borderRadius:8 }}>{error}</div>}

          <div style={{ display:'flex', gap:12 }}>
            <select value={mealType} onChange={e => setMealType(e.target.value)} style={{ padding:'10px 12px', border:'2px solid #e5e7eb', borderRadius:10 }}>
              {['Breakfast','Lunch','Dinner','Snack'].map(m => <option key={m} value={m}>{m}</option>)}
            </select>
            <div style={{ position:'relative', flex:1 }}>
              <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search ingredients..." style={{ width:'100%', padding:'10px 36px 10px 12px', border:'2px solid #e5e7eb', borderRadius:10 }} />
              <Search width={16} height={16} style={{ position:'absolute', right:12, top:10, color:'#9ca3af' }} />
              {loading && <div style={{ position:'absolute', right:36, top:10, fontSize:12, color:'#9ca3af' }}>...</div>}
            </div>
          </div>

          {!!results.length && (
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))', gap:12 }}>
              {results.map(r => (
                <button key={r.id} onClick={()=>addIngredient(r)} style={{ textAlign:'left', border:'1px solid #e5e7eb', borderRadius:10, padding:12, background:'#fff', cursor:'pointer' }}>
                  <div style={{ fontWeight:700 }}>{r.name}</div>
                  <div style={{ fontSize:12, color:'#6b7280' }}>Tap to add</div>
                </button>
              ))}
            </div>
          )}

          <div style={{ display:'grid', gap:8 }}>
            {selected.map(s => (
              <div key={s.id} style={{ display:'flex', gap:12, alignItems:'center', border:'1px solid #e5e7eb', borderRadius:10, padding:10 }}>
                <div style={{ flex:1, fontWeight:600 }}>{s.name}</div>
                <input type="number" value={s.grams} onChange={e=>updateGrams(s.id, e.target.value)} placeholder="grams" style={{ width:120, padding:'8px 10px', border:'2px solid #e5e7eb', borderRadius:10 }} />
                <button onClick={()=>removeSelected(s.id)} style={{ border:'none', background:'transparent', color:'#b91c1c', cursor:'pointer' }}>Remove</button>
              </div>
            ))}
          </div>

          <div style={{ display:'flex', justifyContent:'flex-end' }}>
            <button disabled={loading} onClick={save} style={{ padding:'10px 16px', border:'none', borderRadius:10, background:'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)', color:'#fff', fontWeight:700, cursor:'pointer' }}>
              <Plus width={16} height={16} />
              <span style={{ marginLeft:8 }}>{loading ? 'Saving...' : 'Save Meal'}</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
