import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import toast from 'react-hot-toast'

export default function SignUp() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', full_name: '', institution: '' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { error } = await supabase.auth.signUp({
        email: form.email,
        password: form.password,
        options: { data: { full_name: form.full_name, institution: form.institution } }
      })
      if (error) throw error
      toast.success('Account created! Check your email to verify.')
      navigate('/signin')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0a0d0f', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: 20, fontWeight: 600, color: '#e8e6e0' }}>Iteragen</div>
          <div style={{ fontFamily: 'DM Mono', fontSize: 9, color: '#1D9E75', letterSpacing: '1.5px', textTransform: 'uppercase', marginTop: 4 }}>Create your account</div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[
            { key: 'full_name', label: 'Full name', type: 'text', placeholder: 'Dr. Jane Smith' },
            { key: 'institution', label: 'Institution', type: 'text', placeholder: 'University / Hospital / Lab' },
            { key: 'email', label: 'Email', type: 'email', placeholder: 'you@university.edu' },
            { key: 'password', label: 'Password', type: 'password', placeholder: '········' }
          ].map(field => (
            <div key={field.key}>
              <label style={{ fontSize: 11, color: 'rgba(232,230,224,0.5)', display: 'block', marginBottom: 6, fontFamily: 'DM Mono', letterSpacing: '0.5px' }}>{field.label}</label>
              <input
                type={field.type}
                placeholder={field.placeholder}
                value={form[field.key]}
                onChange={e => setForm({ ...form, [field.key]: e.target.value })}
                required
                style={{
                  width: '100%', padding: '10px 12px',
                  background: '#0f1316', border: '0.5px solid rgba(255,255,255,0.1)',
                  borderRadius: 6, color: '#e8e6e0', fontSize: 13,
                  outline: 'none'
                }}
              />
            </div>
          ))}

          <button type="submit" disabled={loading} style={{
            padding: '11px', borderRadius: 6, background: loading ? '#0f6e56' : '#1D9E75',
            border: 'none', color: '#fff', fontSize: 14, fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer', marginTop: 6
          }}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'rgba(232,230,224,0.4)' }}>
          Already have an account?{' '}
          <Link to="/signin" style={{ color: '#1D9E75', textDecoration: 'none' }}>Sign in</Link>
        </p>

        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 10, color: 'rgba(232,230,224,0.2)', fontFamily: 'DM Mono' }}>
          Research use only · Not for clinical decisions
        </p>
      </div>
    </div>
  )
}
