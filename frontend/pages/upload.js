import Header from '../components/Header'
import Footer from '../components/Footer'
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function Upload(){
  const [file, setFile] = useState(null)
  const router = useRouter()

  async function submit(e){
    e.preventDefault()
    if(!file){ alert('Choose a PDF'); return }
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch('/api/upload', { method:'POST', body: fd })
    if(res.ok){
      alert('Uploaded')
      router.push('/dashboard')
    } else {
      alert('Upload failed')
    }
  }

  return (
    <>
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h2 className="text-xl font-semibold mb-4">Upload Health Report (PDF)</h2>
        <form onSubmit={submit} className="bg-white p-4 rounded shadow space-y-3">
          <input accept="application/pdf" onChange={(e)=>setFile(e.target.files?.[0]||null)} type="file" />
          <div>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded" type="submit">Submit</button>
          </div>
        </form>
      </main>
      <Footer />
    </>
  )
}
