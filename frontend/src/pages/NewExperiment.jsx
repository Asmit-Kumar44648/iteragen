import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext'
import { jobsAPI, proteinsAPI } from '../lib/api'
import toast from 'react-hot-toast'

const QUICK_TARGETS = [
  { label: 'EGFR — Lung cancer', pdb: '1IEP', protein: 'EGFR kinase', disease: 'lung cancer' },
  { label: 'BCR-ABL — Leukemia', pdb: '2HYY', protein: 'BCR-ABL kinase', disease: 'leukemia' },
  { label: 'BRAF — Melanoma', pdb: '1UWH', protein: 'BRAF kinase', disease: 'melanoma' },
  { label: 'CDK2 — Breast cancer', pdb: '1HCL', protein: 'CDK2 kinase', disease: 'breast cancer' }
]

export default function NewExperiment() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [proteinInfo, setProteinInfo] = useState(null)
  const [form, setForm] = useState({ title: '', disease: '', target_protein: '', pdb_id: '' })

  const applyQuick = (target) => {
    setForm({ title: target.label, disease: target.disease, target_protein: target.protein, pdb_id: target.pdb })
    setProteinInfo(null)
  }

  const verifyProtein = async () => {
    if (!form.pdb_id) return
    setVerifying(true)
    try {
      const res = await proteinsAPI.getInfo(form.pdb_id)
      setProteinInfo(res.data)
      toast.success('Protein structure verified')
    } catch {
      toast.error('PDB ID not found in RCSB')
      setProteinInfo(null)
    } finally {
      setVerifying(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.pdb_id || !form.target_protein || !form.disease) {
      toast.error('Please fill all fields')
      return
    }
    setLoading(true)
    try {
      const res = await jobsAPI.submit({ user_id: user.id, ...form })
      toast.success('Experiment submitted!')
      navigate(`/experiment/${res.data.experiment_id}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0a0d0f' }}>
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 32px', borderBottom: '0.5px solid rgba(255,255,255,0.07)' }}>
        <div style={{ fontSize: 15, fontWeight: 600, color: '#e8e6e0', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>← Dashboard</div>
        <div style={{ fontFamily: 'DM Mono', fontSize: 9, color: '#1D9E75', letterSpacing: '1.5px', textTransform: 'uppercase' }}>New experiment</div>
      </nav>

      <div style={{ maxWidth: 600, margin: '0 auto', padding: '40px 32px' }}>
        <h1 style={{ fontSize: 22, fontWeight: 500, color: '#e8e6e0', marginBottom: 8 }}>Configure experiment</h1>
        <p style={{ fontSize: 13, color: 'rgba(232,230,224,0.4)', marginBottom: 32 }}>The AI agent will fetch literature, screen molecules, run docking, and deliver a ranked report.</p>

        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 11, color: 'rgba(232,230,224,0.4)', fontFamily: 'DM Mono', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: 10 }}>Quick targets</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {QUICK_TARGETS.map(t => (
              <button key={t.pdb} onClick={() => applyQuick(t)} style={{
                padding: '5px 12px', borderRadius: 20,
                border: form.pdb_id === t.pdb ? '0.5px solid #1D9E75' : '0.5px solid rgba(255,255,255,0.1)',
                background: form.pdb_id === t.pdb ? 'rgba(29,158,117,0.1)' : 'transparent',
                color: form.pdb_id === t.pdb ? '#1D9E75' : 'rgba(232,230,224,0.5)',
                fontSize: 11, cursor: 'pointer', fontFamily: 'DM Mono'
              }}>{t.label}</button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { key: 'title', label: 'Experiment title', placeholder: 'EGFR lung cancer screen' },
            { key: 'disease', label: 'Disease / indication', placeholder: 'lung cancer' },
            { key: 'target_protein', label: 'Target protein', placeholder: 'EGFR kinase' },
          ].map(field => (
            <div key={field.key}>
              <label style={{ fontSize: 11, color: 'rgba(232,230,224,0.5)', display: 'block', marginBottom: 6, fontFamily: 'DM Mono', letterSpacing: '0.5px' }}>{field.label}</label>
              <input
                value={form[field.key]}
                onChange={e => setForm({ ...form, [field.key]: e.target.value })}
                placeholder={field.placeholder}
                required
                style={{ width: '100%', padding: '10px 12px', background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.1)', borderRadius: 6, color: '#e8e6e0', fontSize: 13, outline: 'none' }}
              />
            </div>
          ))}

          <div>
            <label style={{ fontSize: 11, color: 'rgba(232,230,224,0.5)', display: 'block', marginBottom: 6, fontFamily: 'DM Mono', letterSpacing: '0.5px' }}>PDB ID</label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input
                value={form.pdb_id}
                onChange={e => setForm({ ...form, pdb_id: e.target.value.toUpperCase() })}
                placeholder="1IEP"
                required
                style={{ flex: 1, padding: '10px 12px', background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.1)', borderRadius: 6, color: '#e8e6e0', fontSize: 13, outline: 'none', fontFamily: 'DM Mono' }}
              />
              <button type="button" onClick={verifyProtein} disabled={verifying} style={{ padding: '10px 16px', background: 'transparent', border: '0.5px solid rgba(255,255,255,0.15)', borderRadius: 6, color: 'rgba(232,230,224,0.6)', fontSize: 12, cursor: 'pointer' }}>
                {verifying ? 'Verifying...' : 'Verify'}
              </button>
            </div>
            {proteinInfo && (
              <div style={{ marginTop: 8, padding: '8px 12px', background: 'rgba(29,158,117,0.08)', border: '0.5px solid rgba(29,158,117,0.2)', borderRadius: 6 }}>
                <div style={{ fontSize: 11, color: '#1D9E75', fontFamily: 'DM Mono' }}>✓ {proteinInfo.title}</div>
                <div style={{ fontSize: 10, color: 'rgba(232,230,224,0.4)', marginTop: 2 }}>{proteinInfo.method} · {proteinInfo.organism}</div>
              </div>
            )}
          </div>

          <div style={{ padding: '10px 12px', background: 'rgba(239,159,39,0.08)', border: '0.5px solid rgba(239,159,39,0.2)', borderRadius: 6, fontSize: 11, color: 'rgba(239,159,39,0.8)', fontFamily: 'DM Mono', marginTop: 4 }}>
            All results are in silico predictions. Wet lab validation required before drawing conclusions.
          </div>

          <button type="submit" disabled={loading} style={{ padding: '12px', borderRadius: 6, background: loading ? '#0f6e56' : '#1D9E75', border: 'none', color: '#fff', fontSize: 14, fontWeight: 500, cursor: loading ? 'not-allowed' : 'pointer', marginTop: 4 }}>
            {loading ? 'Submitting...' : 'Run experiment →'}
          </button>
        </form>
      </div>
    </div>
  )
}
