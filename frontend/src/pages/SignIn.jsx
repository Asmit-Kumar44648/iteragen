import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import toast from 'react-hot-toast'

export default function SignIn() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ email: '', password: '' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: form.email,
        password: form.password
      })
      if (error) throw error
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0a0d0f', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 380 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: 20, fontWeight: 600, color: '#e8e6e0' }}>Iteragen</div>
          <div style={{ fontFamily: 'DM Mono', fontSize: 9, color: '#1D9E75', letterSpacing: '1.5px', textTransform: 'uppercase', marginTop: 4 }}>Sign in to your account</div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[
            { key: 'email', label: 'Email', type: 'email', placeholder: 'you@university.edu' },
            { key: 'password', label: 'Password', type: 'password', placeholder: '········' }
          ].map(field => (
            <div key={field.key}>
              <label style={{ fontSize: 11, color: 'rgba(232,230,224,0.5)', display: 'block', marginBottom: 6, fontFamily: 'DM Mono' }}>{field.label}</label>
              <input
                type={field.type}
                placeholder={field.placeholder}
                value={form[field.key]}
                onChange={e => setForm({ ...form, [field.key]: e.target.value })}
                required
                style={{
                  width: '100%', padding: '10px 12px',
                  background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.1)',
                  borderRadius: 6, color: '#e8e6e0', fontSize: 13, outline: 'none'
                }}
              />
            </div>
          ))}

          <button type="submit" disabled={loading} style={{
            padding: '11px', borderRadius: 6, background: loading ? '#0f6e56' : '#1D9E75',
            border: 'none', color: '#fff', fontSize: 14, fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer', marginTop: 6
          }}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'rgba(232,230,224,0.4)' }}>
          No account?{' '}
          <Link to="/signup" style={{ color: '#1D9E75', textDecoration: 'none' }}>Create one free</Link>
        </p>
      </div>
    </div>
  )
}
