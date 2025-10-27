export default function handler(req, res){
  if(req.method !== 'POST') return res.status(405).end()
  // In production, save to database.
  const body = req.body
  if(body && body.username && body.password){
    return res.status(200).json({ ok:true })
  }
  res.status(400).json({ ok:false })
}
