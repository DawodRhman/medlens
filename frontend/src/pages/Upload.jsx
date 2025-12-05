import React, {useState, useRef} from 'react'
import axios from 'axios'

export default function Upload({token}){
  const fileRef = useRef()
  const [result,setResult] = useState(null)

  async function submit(e){
    e.preventDefault()
    const file = fileRef.current.files[0]
    const fd = new FormData()
    fd.append('file', file)
    try{
      const res = await axios.post('http://localhost:8000/predict/', fd, {headers: {'Content-Type':'multipart/form-data', Authorization: `Bearer ${token}`}})
      setResult(res.data)
    }catch(e){
      setResult({error: 'prediction failed'})
    }
  }

  return (
    <div>
      <h3>Upload Signal</h3>
      <form onSubmit={submit}>
        <input type="file" ref={fileRef} accept="audio/*" />
        <button>Predict</button>
      </form>
      {result && <pre>{JSON.stringify(result,null,2)}</pre>}
    </div>
  )
}
