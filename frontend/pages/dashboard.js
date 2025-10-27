import Header from '../components/Header'
import Footer from '../components/Footer'
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function Dashboard(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const router = useRouter()

  async function askLLM(e){
    e.preventDefault()
    // Call local API which will be a stub for LLM
    const res = await fetch('/api/llm', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ prompt: query })
    })
    const data = await res.json()
    setResults(prev => [{input: query, output: data.text}, ...prev])
    setQuery('')
  }

  return (
    <>
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Dashboard</h2>
          <button className="px-3 py-2 bg-indigo-600 text-white rounded" onClick={()=>router.push('/upload')}>Upload Reports</button>
        </div>

        <form onSubmit={askLLM} className="mb-6">
          <div className="flex gap-2">
            <input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Ask questions about your health reports..." className="flex-1 p-3 border rounded" />
            <button className="px-4 py-2 bg-indigo-600 text-white rounded" type="submit">Ask</button>
          </div>
        </form>

        <div className="space-y-4">
          {results.map((r, idx) => (
            <div key={idx} className="bg-white p-4 rounded shadow">
              <div className="text-sm text-gray-500 mb-2">You asked: {r.input}</div>
              <div className="whitespace-pre-wrap">{r.output}</div>
            </div>
          ))}
          {results.length === 0 && (
            <div className="text-gray-500">No questions yet. Ask about your reports above.</div>
          )}
        </div>

        {/* Floating button bottom-right */}
        <button onClick={()=>router.push('/upload')} className="fixed bottom-6 right-6 bg-indigo-600 text-white rounded-full w-14 h-14 shadow-lg flex items-center justify-center">
          +
        </button>
      </main>
      <Footer />
    </>
  )
}
