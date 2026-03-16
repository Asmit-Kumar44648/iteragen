import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext'
import { experimentsAPI } from '../lib/api'
import { supabase } from '../lib/supabase'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [experiments, setExperiments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) loadExperiments()
  }, [user])

  const loadExperiments = async () => {
    try {
      const res = await experimentsAPI.list(user.id)
      setExperiments(res.data || [])
    } catch {
      setExperiments([])
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    navigate('/')
  }

  const statusColor = (s) => ({ completed: '#1D9E75', running: '#EF9F27', queued: '#378ADD', failed: '#E24B4A' }[s] || '#888')

  return (
    <div style={{ minHeight: '100vh', background: '#0a0d0f' }}>
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 32px', borderBottom: '0.5px solid rgba(255,255,255,0.07)' }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 600, color: '#e8e6e0' }}>Iteragen</div>
          <div style={{ fontFamily: 'DM Mono', fontSize: 9, color: '#1D9E75', letterSpacing: '1.5px', textTransform: 'uppercase' }}>Dashboard</div>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <span style={{ fontSize: 12, color: 'rgba(232,230,224,0.4)', fontFamily: 'DM Mono' }}>{user?.email}</span>
          <button onClick={() => navigate('/experiment/new')} style={{ padding: '7px 16px', background: '#1D9E75', border: 'none', borderRadius: 6, color: '#fff', fontSize: 13, cursor: 'pointer', fontWeight: 500 }}>+ New experiment</button>
          <button onClick={signOut} style={{ padding: '7px 14px', background: 'transparent', border: '0.5px solid rgba(255,255,255,0.1)', borderRadius: 6, color: 'rgba(232,230,224,0.5)', fontSize: 13, cursor: 'pointer' }}>Sign out</button>
        </div>
      </nav>

      <div style={{ maxWidth: 900, margin: '0 auto', padding: '40px 32px' }}>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 22, fontWeight: 500, color: '#e8e6e0', marginBottom: 6 }}>Your experiments</h1>
          <p style={{ fontSize: 13, color: 'rgba(232,230,224,0.4)' }}>All results are in silico predictions — experimental validation required.</p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'rgba(232,230,224,0.3)', fontFamily: 'DM Mono', fontSize: 12 }}>Loading...</div>
        ) : experiments.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 80, border: '0.5px dashed rgba(255,255,255,0.1)', borderRadius: 10 }}>
            <div style={{ fontSize: 13, color: 'rgba(232,230,224,0.3)', marginBottom: 20 }}>No experiments yet</div>
            <button onClick={() => navigate('/experiment/new')} style={{ padding: '10px 20px', background: '#1D9E75', border: 'none', borderRadius: 6, color: '#fff', fontSize: 13, cursor: 'pointer' }}>Run your first experiment</button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {experiments.map(exp => (
              <div key={exp.id} onClick={() => navigate(`/experiment/${exp.id}`)} style={{
                background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.07)',
                borderRadius: 8, padding: '16px 20px', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                transition: 'border-color 0.15s'
              }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 500, color: '#e8e6e0', marginBottom: 4 }}>{exp.title}</div>
                  <div style={{ fontSize: 11, color: 'rgba(232,230,224,0.4)', fontFamily: 'DM Mono' }}>
                    {exp.target_protein} · {exp.pdb_id} · {new Date(exp.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  {exp.top_score && (
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 16, fontWeight: 500, color: '#1D9E75', fontFamily: 'DM Mono' }}>{exp.top_score}</div>
                      <div style={{ fontSize: 9, color: 'rgba(232,230,224,0.3)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>kcal/mol</div>
                    </div>
                  )}
                  <div style={{ fontSize: 10, padding: '3px 8px', borderRadius: 4, fontFamily: 'DM Mono', background: `${statusColor(exp.status)}22`, color: statusColor(exp.status) }}>{exp.status}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
