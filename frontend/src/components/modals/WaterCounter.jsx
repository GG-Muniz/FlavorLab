import { useEffect, useRef, useState } from 'react';
import { X, Droplets, Plus } from 'lucide-react';
import { updateDailyWaterGoal, logWaterIntake, fetchWaterSummary } from '../../services/waterApi';

const WaterCounter = ({ isOpen, onClose, onDataUpdate }) => {
  const [goalMl, setGoalMl] = useState('');
  const [intakeMl, setIntakeMl] = useState('');
  const [savedGoal, setSavedGoal] = useState(null);
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isOpen) return;
    (async () => {
      try {
        setIsLoading(true); setError('');
        const today = new Date().toISOString().slice(0,10);
        const summary = await fetchWaterSummary(today).catch(() => ({ goal_ml: null, total_intake_ml: 0, entries: [], percentage: 0 }));
        if (summary?.goal_ml != null) setSavedGoal(summary.goal_ml);
        setEntries(Array.isArray(summary?.entries) ? summary.entries : []);
      } catch (e) {
        setError(e?.message || 'Failed to load water data. Using offline mode.');
      } finally { setIsLoading(false); }
    })();
  }, [isOpen]);

  const totalIntake = entries.reduce((s, e) => s + (e?.volume_ml || 0), 0);
  const percentage = savedGoal ? Math.min(100, Math.round((totalIntake / savedGoal) * 100)) : 0;
  const remaining = savedGoal ? Math.max(0, savedGoal - totalIntake) : null;

  async function handleSaveGoal() {
    if (!goalMl || isNaN(goalMl)) return;
    try {
      setIsLoading(true); setError('');
      await updateDailyWaterGoal(Number(goalMl));
      setSavedGoal(Number(goalMl));
      setGoalMl('');
      onDataUpdate && onDataUpdate();
    } catch (e) {
      setError(e?.message || 'Failed to save water goal');
    } finally { setIsLoading(false); }
  }

  async function handleAddIntake() {
    if (!intakeMl || isNaN(intakeMl)) return;
    try {
      setIsLoading(true); setError('');
      const entry = await logWaterIntake(Number(intakeMl));
      setEntries(prev => [{ id: entry.id, volume_ml: entry.volume_ml, created_at: entry.created_at, entry_date: entry.entry_date }, ...prev]);
      setIntakeMl('');
      onDataUpdate && onDataUpdate();
    } catch (e) {
      setError(e?.message || 'Failed to log water');
    } finally { setIsLoading(false); }
  }

  if (!isOpen) return null;

  return (
    <>
      <div onClick={onClose} style={{ position:'fixed', inset:0, background:'rgba(0,0,0,0.5)', zIndex:1001 }} />
      <div style={{ position:'fixed', top:'50%', left:'50%', transform:'translate(-50%,-50%)', width:'90%', maxWidth:600, background:'#fff', borderRadius:24, border:'1px solid #e5e7eb', zIndex:1002 }}>
        <div style={{ background:'linear-gradient(135deg,#22c55e 0%,#16a34a 100%)', borderTopLeftRadius:24, borderTopRightRadius:24, padding:'28px 24px', position:'relative' }}>
          <button onClick={onClose} style={{ position:'absolute', top:12, right:12, width:32, height:32, background:'rgba(255,255,255,0.2)', border:'none', borderRadius:'50%', cursor:'pointer' }}>
            <X width={18} height={18} color="#fff" />
          </button>
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            <div style={{ width:48, height:48, background:'rgba(255,255,255,0.2)', borderRadius:12, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <Droplets width={24} height={24} color="#fff" />
            </div>
            <h2 style={{ margin:0, color:'#fff' }}>Water Counter</h2>
          </div>
        </div>
        <div style={{ padding:24 }}>
          {error && <div style={{ marginBottom:12, padding:'8px 12px', background:'#fef2f2', border:'1px solid #fecaca', color:'#991b1b', borderRadius:8 }}>{error}</div>}

          {savedGoal && (
            <div style={{ marginBottom:16, padding:16, background:'#f0fdf4', border:'1px solid #bbf7d0', borderRadius:12 }}>
              <div style={{ display:'flex', justifyContent:'space-between' }}>
                <div><div style={{ fontSize:12, color:'#6b7280' }}>Goal</div><div style={{ fontWeight:700 }}>{savedGoal} ml</div></div>
                <div><div style={{ fontSize:12, color:'#6b7280' }}>Intake</div><div style={{ fontWeight:700 }}>{totalIntake} ml</div></div>
                <div><div style={{ fontSize:12, color:'#6b7280' }}>Remaining</div><div style={{ fontWeight:700, color: remaining >= 0 ? '#16a34a' : '#ef4444' }}>{remaining ?? 0} ml</div></div>
              </div>
              <div style={{ marginTop:10, height:8, background:'#fff', borderRadius:999 }}>
                <div style={{ height:'100%', width:`${percentage}%`, background:'linear-gradient(90deg,#22c55e 0%,#16a34a 100%)', borderRadius:999 }} />
              </div>
            </div>
          )}

          <div style={{ marginBottom:16 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>
              <Droplets width={18} height={18} color="#22c55e" />
              <h3 style={{ margin:0 }}>Daily Water Goal</h3>
            </div>
            <div style={{ display:'flex', gap:12 }}>
              <input type="number" value={goalMl} onChange={(e)=>setGoalMl(e.target.value)} placeholder="Enter goal (ml)" style={{ flex:1, padding:'10px 12px', border:'2px solid #e5e7eb', borderRadius:12 }} />
              <button onClick={handleSaveGoal} disabled={isLoading} style={{ padding:'10px 16px', background:'#22c55e', color:'#fff', border:'none', borderRadius:12, fontWeight:700, cursor:'pointer' }}>{isLoading ? 'Saving...' : 'Set Goal'}</button>
            </div>
          </div>

          <div style={{ marginBottom:16 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>
              <Droplets width={18} height={18} color="#22c55e" />
              <h3 style={{ margin:0 }}>Log Water Intake</h3>
            </div>
            <div style={{ display:'flex', gap:12 }}>
              <input type="number" value={intakeMl} onChange={(e)=>setIntakeMl(e.target.value)} placeholder="Volume (ml)" style={{ flex:1, padding:'10px 12px', border:'2px solid #e5e7eb', borderRadius:12 }} />
              <button onClick={handleAddIntake} disabled={isLoading} style={{ padding:'10px 16px', background:'#0ea5e9', color:'#fff', border:'none', borderRadius:12, fontWeight:700, cursor:'pointer', display:'inline-flex', alignItems:'center', gap:8 }}><Plus width={16} height={16} />{isLoading ? 'Adding...' : 'Add'}</button>
            </div>
          </div>

          {entries?.length > 0 && (
            <div>
              <h3 style={{ margin:'0 0 8px 0' }}>Today's Water</h3>
              <div style={{ border:'1px solid #e5e7eb', borderRadius:12, overflow:'hidden' }}>
                {entries.map((e, idx) => (
                  <div key={e.id} style={{ padding:12, display:'flex', justifyContent:'space-between', borderBottom: idx < entries.length-1 ? '1px solid #f3f4f6' : 'none' }}>
                    <span>{new Date(e.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    <span style={{ fontWeight:700 }}>{e.volume_ml} ml</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default WaterCounter;


