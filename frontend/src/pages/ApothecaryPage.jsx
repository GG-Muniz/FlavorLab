import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../context/AuthContext';

// Static MVP data source (can be moved to backend later)
import data from '../static/apothecary.json';
import './ApothecaryPage.css';

export default function ApothecaryPage() {
  const { user } = useAuth();
  const [selectedGoals, setSelectedGoals] = useState([]);

  useEffect(() => {
    const prefs = user?.preferences || {};
    const top = user?.health_goals;
    const goals = Array.isArray(prefs.health_goals)
      ? prefs.health_goals
      : (Array.isArray(top?.selectedGoals) ? top.selectedGoals : (Array.isArray(top) ? top : []));
    setSelectedGoals(goals);
  }, [user]);

  const responses = useMemo(() => {
    // Map pillar ID to name used in provided data keys
    const idToName = {
      1: 'Increased Energy',
      2: 'Improved Digestion',
      3: 'Enhanced Immunity',
      4: 'Better Sleep',
      5: 'Mental Clarity',
      6: 'Heart Health',
      7: 'Muscle Recovery',
      8: 'Inflammation Reduction'
    };
    const allowed = new Set((selectedGoals || []).map(id => idToName[id]).filter(Boolean));
    const all = data?.apothecary_responses || [];
    return all.filter(r => allowed.has(r.health_goal));
  }, [selectedGoals]);

  const goalTagColor = (goal) => {
    const map = {
      'Increased Energy': '#16a34a',
      'Improved Digestion': '#22c55e',
      'Enhanced Immunity': '#0891b2',
      'Better Sleep': '#8b5cf6',
      'Mental Clarity': '#ec4899',
      'Heart Health': '#ef4444',
      'Muscle Recovery': '#0ea5e9',
      'Inflammation Reduction': '#f59e0b'
    };
    return map[goal] || '#22c55e';
  };

  const imageFor = (remedy, goal, sig = 0) => {
    const q = encodeURIComponent(`${remedy}, ${goal}, healthy, wellness`);
    return `https://source.unsplash.com/featured/800x480/?${q}&sig=${sig}`;
  };

  return (
    <div className="apothecary-container">
      <h1 style={{ marginTop: 0, marginBottom: 6, fontWeight: 900, fontSize: 32 }}>Your Apothecary</h1>
      <p style={{ color: 'var(--text-secondary)' }}>Personalized remedies based on your HealthLab goals.</p>

      <div className="apothecary-grid">
        {responses.map((r, idx) => (
          <div key={idx} className="apothecary-card">
            <div className="apothecary-card__image">
              <img
                src={r.image_url || imageFor(r.remedy, r.health_goal, idx)}
                alt={r.remedy}
                loading="lazy"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onError={(e)=>{
                  const fallback1 = imageFor(r.remedy, r.health_goal, idx + 1);
                  const fallback2 = `https://picsum.photos/seed/${encodeURIComponent(r.remedy)}-${idx}/800/480`;
                  if (!e.currentTarget.dataset.f1) {
                    e.currentTarget.dataset.f1 = '1';
                    e.currentTarget.src = fallback1;
                    return;
                  }
                  if (!e.currentTarget.dataset.f2) {
                    e.currentTarget.dataset.f2 = '1';
                    e.currentTarget.src = fallback2;
                    return;
                  }
                  e.currentTarget.src = '/Healthlab.png';
                }}
              />
            </div>
            <div className="apothecary-card__body">
              <div className="apothecary-card__goal">
                <span style={{ background: `${goalTagColor(r.health_goal)}20`, color: goalTagColor(r.health_goal) }}>{r.health_goal}</span>
              </div>
              <h3 style={{ marginTop: 6, marginBottom: 8 }}>{r.remedy}</h3>
              <div style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 8 }}>Serving size: {r.serving_size}</div>
              <div className="apothecary-card__section-title">Ingredients</div>
              <ul className="apothecary-card__list">
                {Object.entries(r.ingredients || {}).map(([name, qty]) => (
                  <li key={name}><span style={{ fontWeight: 600 }}>{name}</span>: <span>{qty}</span></li>
                ))}
              </ul>
              <div className="apothecary-card__section-title">Preparation</div>
              <div>{r.preparation}</div>
              <div className="apothecary-card__section-title">Benefit</div>
              <div>{r.benefit}</div>
              <div className="apothecary-card__section-title">Timing</div>
              <div>{r.timing}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


