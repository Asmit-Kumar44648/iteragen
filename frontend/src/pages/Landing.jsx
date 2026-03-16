import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div style={{ minHeight: '100vh', background: '#0a0d0f' }}>
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '18px 40px', borderBottom: '0.5px solid rgba(255,255,255,0.07)',
        position: 'sticky', top: 0, background: 'rgba(10,13,15,0.95)', zIndex: 100
      }}>
        <div>
          <div style={{ fontSize: 16, fontWeight: 600, color: '#e8e6e0' }}>Iteragen</div>
          <div style={{ fontFamily: 'DM Mono', fontSize: 9, color: '#1D9E75', letterSpacing: '1.5px', textTransform: 'uppercase' }}>AI Drug Discovery</div>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button onClick={() => navigate('/signin')} style={{
            padding: '7px 16px', border: '0.5px solid rgba(255,255,255,0.15)',
            borderRadius: 6, background: 'transparent', color: 'rgba(232,230,224,0.7)',
            cursor: 'pointer', fontSize: 13
          }}>Sign in</button>
          <button onClick={() => navigate('/signup')} style={{
            padding: '7px 18px', border: 'none', borderRadius: 6,
            background: '#1D9E75', color: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 500
          }}>Get started free</button>
        </div>
      </nav>

      <div style={{ maxWidth: 860, margin: '0 auto', padding: '80px 40px', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          fontFamily: 'DM Mono', fontSize: 10, letterSpacing: '1.5px',
          textTransform: 'uppercase', color: '#1D9E75',
          padding: '5px 12px', border: '0.5px solid rgba(29,158,117,0.3)',
          borderRadius: 20, marginBottom: 28
        }}>
          <div style={{ width: 5, height: 5, borderRadius: '50%', background: '#1D9E75' }}></div>
          Research Use Only · In silico platform
        </div>

        <h1 style={{ fontSize: 52, fontWeight: 600, lineHeight: 1.1, letterSpacing: '-1.5px', marginBottom: 20 }}>
          Drug discovery,<br />driven by <span style={{ color: '#1D9E75' }}>autonomous AI</span>
        </h1>

        <p style={{ fontSize: 16, color: 'rgba(232,230,224,0.5)', lineHeight: 1.7, maxWidth: 560, margin: '0 auto 36px' }}>
          An AI agent that designs experiments, runs real molecular docking, reads the literature, and iterates — without a $40,000 software license.
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 60 }}>
          <button onClick={() => navigate('/signup')} style={{
            padding: '11px 24px', borderRadius: 8, background: '#1D9E75',
            border: 'none', color: '#fff', fontSize: 14, fontWeight: 500, cursor: 'pointer'
          }}>Start your first experiment →</button>
          <button onClick={() => navigate('/signin')} style={{
            padding: '11px 24px', borderRadius: 8,
            border: '0.5px solid rgba(255,255,255,0.15)',
            background: 'transparent', color: 'rgba(232,230,224,0.7)', fontSize: 14, cursor: 'pointer'
          }}>Sign in</button>
        </div>

        <div style={{
          background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.08)',
          borderRadius: 10, overflow: 'hidden', maxWidth: 680, margin: '0 auto', textAlign: 'left'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 14px', borderBottom: '0.5px solid rgba(255,255,255,0.06)', background: '#0c1013' }}>
            <div style={{ width: 9, height: 9, borderRadius: '50%', background: '#ff5f57' }}></div>
            <div style={{ width: 9, height: 9, borderRadius: '50%', background: '#febc2e' }}></div>
            <div style={{ width: 9, height: 9, borderRadius: '50%', background: '#28c840' }}></div>
            <span style={{ fontFamily: 'DM Mono', fontSize: 10, color: 'rgba(255,255,255,0.2)', marginLeft: 8 }}>iteragen · agent log · live</span>
          </div>
          <div style={{ padding: '16px 20px', fontFamily: 'DM Mono', fontSize: 11, lineHeight: 1.9 }}>
            <div><span style={{ color: '#1D9E75' }}>HYP</span> <span style={{ color: '#e8e6e0' }}>EGFR T790M resistance — targeting C797 covalent binding site</span></div>
            <div style={{ color: 'rgba(232,230,224,0.4)', paddingLeft: 20 }}>literature support: <span style={{ color: '#1D9E75' }}>PMID 31447393</span> · confidence: high</div>
            <div><span style={{ color: '#1D9E75' }}>EXP</span> <span style={{ color: '#e8e6e0' }}>docking erlotinib-analog-7 · ensemble · 12 conformers</span></div>
            <div style={{ color: 'rgba(232,230,224,0.4)', paddingLeft: 20 }}>binding affinity: <span style={{ color: '#1D9E75' }}>−9.4 kcal/mol</span> · ADMET: <span style={{ color: '#1D9E75' }}>pass</span></div>
            <div><span style={{ color: '#1D9E75' }}>THK</span> <span style={{ color: '#e8e6e0' }}>strong result · exploring F-substitution for ERBB2 selectivity</span></div>
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', padding: '10px 40px 20px', fontFamily: 'DM Mono', fontSize: 9, color: 'rgba(232,230,224,0.2)' }}>
        Iteragen is a research hypothesis generation tool only. All outputs are in silico predictions and require experimental validation. Not for clinical use.
      </div>
    </div>
  )
}
