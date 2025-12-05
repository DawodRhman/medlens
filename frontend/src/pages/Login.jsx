import React, {useState} from 'react'
import axios from 'axios'

export default function Login({onLogin}){
  const [user,setUser]=useState('admin')
  const [pass,setPass]=useState('admin')
  const [err,setErr]=useState(null)

  async function submit(e){
    e.preventDefault()
    try{
      const res = await axios.post('http://localhost:8000/auth/login', {username: user, password: pass})
      onLogin(res.data.access_token)
    }catch(e){
      setErr('Login failed')
    }
  }

  return (
    <div className="login">
      <h2>MedLens Login</h2>
      <form onSubmit={submit}>
        <input value={user} onChange={e=>setUser(e.target.value)} />
        <input value={pass} onChange={e=>setPass(e.target.value)} type="password" />
        <button type="submit">Login</button>
      </form>
      {err && <div className="error">{err}</div>}
    </div>
  )
}
