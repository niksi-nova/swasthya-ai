export default async function handler(req, res){
  if(req.method !== 'POST') return res.status(405).end()
  const { prompt } = req.body
  // This is a stubbed LLM response. Replace with real LLM call.
  const text = `Simulated LLM answer for prompt: "${prompt}"\n\n(Replace /api/llm with your real LLM integration.)`
  res.status(200).json({ text })
}
