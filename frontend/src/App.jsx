import React, {useState} from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

export default function App(){
  const [token, setToken] = useState(null)
  if(!token) return <Login onLogin={setToken} />
  return <Dashboard token={token} onLogout={() => setToken(null)} />
}
