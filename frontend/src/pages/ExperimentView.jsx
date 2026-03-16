import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobsAPI } from '../lib/api'

const logColor = { hypothesis: '#1D9E75', experiment: '#378ADD', result: '#e8e6e0', thinking: '#EF9F27', error: '#E24B4A' }
const logBg = { hypothesis: 'rgba(29,158,117,0.08)', experiment: 'rgba(55,138,221,0.08)', result: 'rgba(255,255,255,0.03)', thinking: 'rgba(239,159,39,0.08)', error: 'rgba(226,75,74,0.08)' }

export default function ExperimentView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [experiment, setExperiment] = useState(null)
  const [results, setResults] = useState([])
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState('loading')
  const [report, setReport] = useState(null)

  useEffect(() => {
    loadData()
    const interval = setInterval(() => {
      if (!['completed', 'failed'].includes(status)) loadData()
    }, 4000)
    return () => clearInterval(interval)
  }, [id, status])

  const loadData = async () => {
    try {
      const statusRes = await jobsAPI.getStatus(id)
      setStatus(statusRes.data?.db_status?.status || statusRes.data?.status || 'unknown')

      const resultRes = await jobsAPI.getResult(id)
      if (resultRes.data) {
        setExperiment(resultRes.data.experiment || null)
        setResults(resultRes.data.results || [])
        setLogs(resultRes.data.logs || [])
        if (resultRes.data.final_report) setReport(resultRes.data.final_report)
      }
    } catch {}
  }

  const statusColor = { completed: '#1D9E75', running: '#EF9F27', queued: '#378ADD', failed: '#E24B4A' }

  return (
    <div style={{ minHeight: '100vh', background: '#0a0d0f' }}>
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 32px', borderBottom: '0.5px solid rgba(255,255,255,0.07)' }}>
        <div style={{ fontSize: 14, color: 'rgba(232,230,224,0.5)', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>← Dashboard</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {status === 'running' && <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#EF9F27', animation: 'pulse 1.4s ease-in-out infinite' }}></div>}
          <span style={{ fontSize: 11, fontFamily: 'DM Mono', color: statusColor[status] || '#888', padding: '3px 8px', background: `${statusColor[status]}22`, borderRadius: 4 }}>{status}</span>
        </div>
      </nav>

      <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px', display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <h1 style={{ fontSize: 18, fontWeight: 500, color: '#e8e6e0', marginBottom: 4 }}>
              {experiment?.title || 'Loading experiment...'}
            </h1>
            <div style={{ fontSize: 11, color: 'rgba(232,230,224,0.4)', fontFamily: 'DM Mono' }}>
              {experiment?.pdb_id} · {experiment?.target_protein}
            </div>
          </div>

          <div style={{ background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.07)', borderRadius: 8, overflow: 'hidden' }}>
            <div style={{ padding: '10px 14px', borderBottom: '0.5px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 11, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.5)' }}>Agent reasoning log</span>
              <span style={{ fontSize: 9, fontFamily: 'DM Mono', color: '#1D9E75' }}>{logs.length} entries</span>
            </div>
            <div style={{ padding: 10, maxHeight: 320, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}>
              {logs.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: 'rgba(232,230,224,0.2)', fontSize: 12, fontFamily: 'DM Mono' }}>
                  {status === 'queued' ? 'Waiting to start...' : 'No logs yet'}
                </div>
              ) : logs.map(log => (
                <div key={log.id} style={{ display: 'flex', gap: 8, padding: '6px 8px', borderRadius: 4, background: logBg[log.log_type] || 'transparent', fontSize: 11, lineHeight: 1.5 }}>
                  <span style={{ fontFamily: 'DM Mono', fontSize: 9, padding: '2px 5px', borderRadius: 3, background: `${logColor[log.log_type]}22`, color: logColor[log.log_type], flexShrink: 0, alignSelf: 'flex-start', marginTop: 1, textTransform: 'uppercase' }}>{log.log_type?.slice(0, 3)}</span>
                  <span style={{ color: '#e8e6e0' }}>{log.content}</span>
                </div>
              ))}
            </div>
          </div>

          {results.length > 0 && (
            <div>
              <div style={{ fontSize: 10, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.3)', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: 10 }}>Top candidates</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                {results.slice(0, 6).map((r, i) => (
                  <div key={r.id} style={{ background: '#0f1316', border: i === 0 ? '1px solid #1D9E75' : '0.5px solid rgba(255,255,255,0.07)', borderRadius: 8, padding: 12 }}>
                    <div style={{ fontSize: 9, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.3)', marginBottom: 4 }}>#{r.rank || i + 1}{i === 0 ? ' · best' : ''}</div>
                    <div style={{ fontSize: 12, fontWeight: 500, color: '#e8e6e0', marginBottom: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.molecule_name}</div>
                    <div style={{ fontSize: 18, fontWeight: 500, fontFamily: 'DM Mono', color: '#e8e6e0' }}>{r.binding_affinity} <span style={{ fontSize: 10, color: 'rgba(232,230,224,0.3)' }}>kcal/mol</span></div>
                    <div style={{ height: 3, background: 'rgba(255,255,255,0.06)', borderRadius: 2, marginTop: 8, overflow: 'hidden' }}>
                      <div style={{ height: '100%', background: '#1D9E75', borderRadius: 2, width: `${Math.min(100, Math.abs(r.binding_affinity || 0) * 10)}%` }}></div>
                    </div>
                    <div style={{ display: 'flex', gap: 4, marginTop: 6 }}>
                      {r.admet_pass && <span style={{ fontSize: 9, padding: '2px 5px', borderRadius: 3, background: 'rgba(29,158,117,0.12)', color: '#1D9E75', fontFamily: 'DM Mono' }}>admet ✓</span>}
                      {r.molecular_weight && <span style={{ fontSize: 9, padding: '2px 5px', borderRadius: 3, background: 'rgba(255,255,255,0.05)', color: 'rgba(232,230,224,0.4)', fontFamily: 'DM Mono' }}>{Math.round(r.molecular_weight)} Da</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {experiment && (
            <div style={{ background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.07)', borderRadius: 8, padding: 14 }}>
              <div style={{ fontSize: 9, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.3)', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: 10 }}>Target</div>
              <div style={{ fontSize: 13, fontWeight: 500, color: '#e8e6e0', marginBottom: 4 }}>{experiment.target_protein}</div>
              <div style={{ fontSize: 10, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.4)' }}>{experiment.pdb_id}</div>
              <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
                {[['screened', results.length], ['disease', experiment.disease]].map(([k, v]) => (
                  <div key={k} style={{ flex: 1, background: 'rgba(255,255,255,0.03)', borderRadius: 6, padding: '6px 8px', textAlign: 'center' }}>
                    <div style={{ fontSize: 13, fontWeight: 500, color: '#e8e6e0' }}>{v}</div>
                    <div style={{ fontSize: 9, color: 'rgba(232,230,224,0.3)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{k}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report && (
            <div style={{ background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.07)', borderRadius: 8, padding: 14 }}>
              <div style={{ fontSize: 9, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.3)', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: 10 }}>Final report</div>
              <div style={{ fontSize: 12, color: 'rgba(232,230,224,0.7)', lineHeight: 1.6, marginBottom: 10 }}>{report.executive_summary}</div>
              {report.citations?.length > 0 && (
                <div>
                  <div style={{ fontSize: 9, fontFamily: 'DM Mono', color: 'rgba(232,230,224,0.3)', marginBottom: 6 }}>Citations</div>
                  {report.citations.map((c, i) => (
                    <div key={i} style={{ fontSize: 10, color: '#378ADD', fontFamily: 'DM Mono', marginBottom: 3 }}>PMID {c}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div style={{ padding: '10px 12px', background: 'rgba(239,159,39,0.06)', border: '0.5px solid rgba(239,159,39,0.15)', borderRadius: 6, fontSize: 10, color: 'rgba(239,159,39,0.7)', fontFamily: 'DM Mono', lineHeight: 1.5 }}>
            Research use only. All results require wet lab validation.
          </div>
        </div>
      </div>

      <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }`}</style>
    </div>
  )
}
