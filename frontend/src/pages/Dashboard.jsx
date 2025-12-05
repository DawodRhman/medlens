import React from 'react'
import Upload from './Upload'

export default function Dashboard({token, onLogout}){
  return (
    <div className="dashboard">
      <header>
        <h1>MedLens Dashboard</h1>
        <button onClick={onLogout}>Logout</button>
      </header>
      <main>
        <Upload token={token} />
      </main>
    </div>
  )
}
