import { useState } from 'react'
import Header from '../components/Header'
import Footer from '../components/Footer'
import { useRouter } from 'next/router'

export default function Home(){
  const [isSignup, setIsSignup] = useState(false)
  const [form, setForm] = useState({
    name:'', age:'', username:'', password:'', disease:'', email:'', phone:'', foodHabits:'', gender:''
  })
  const router = useRouter()

  const change = (e) => setForm({...form, [e.target.name]: e.target.value})

  async function handleLogin(e){
    e.preventDefault()
    // API call to /api/auth/login
    const res = await fetch('/api/auth/login', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ username: form.username, password: form.password })
    })
    if(res.ok){
      router.push('/dashboard')
    } else {
      alert('Login failed')
    }
  }

  async function handleSignup(e){
    e.preventDefault()
    const res = await fetch('/api/auth/signup', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(form)
    })
    if(res.ok){
      router.push('/dashboard')
    } else {
      alert('Sign up failed')
    }
  }

  return (
    <>
      <Header />
      <main className="max-w-xl mx-auto px-4 py-10">
        <div className="bg-white shadow rounded p-6">
          <h1 className="text-2xl font-semibold mb-4">{isSignup ? 'Sign up' : 'Login'}</h1>
          <form onSubmit={isSignup ? handleSignup : handleLogin} className="space-y-3">
            {isSignup && (
              <>
                <input name="name" value={form.name} onChange={change} required placeholder="Name" className="w-full p-2 border rounded" />
                <input name="age" value={form.age} onChange={change} required placeholder="Age" className="w-full p-2 border rounded" />
              </>
            )}
            <input name="username" value={form.username} onChange={change} required placeholder="Username" className="w-full p-2 border rounded" />
            <input name="password" value={form.password} onChange={change} required type="password" placeholder="Password" className="w-full p-2 border rounded" />
            {isSignup && (
              <>
                <input name="disease" value={form.disease} onChange={change} placeholder="Disease / history" className="w-full p-2 border rounded" />
                <input name="email" value={form.email} onChange={change} required placeholder="Email" className="w-full p-2 border rounded" />
                <input name="phone" value={form.phone} onChange={change} placeholder="Phone number" className="w-full p-2 border rounded" />
                <input name="foodHabits" value={form.foodHabits} onChange={change} placeholder="Food habits" className="w-full p-2 border rounded" />
                <select name="gender" value={form.gender} onChange={change} className="w-full p-2 border rounded">
                  <option value="">Select gender</option>
                  <option>Female</option>
                  <option>Male</option>
                  <option>Other</option>
                </select>
              </>
            )}
            <div className="flex items-center justify-between">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded" type="submit">{isSignup ? 'Sign up' : 'Login'}</button>
              <button type="button" onClick={()=>setIsSignup(!isSignup)} className="text-sm text-indigo-600 underline">
                {isSignup ? 'Have an account? Login' : 'No account? Sign up'}
              </button>
            </div>
          </form>
        </div>
      </main>
      <Footer />
    </>
  )
}
