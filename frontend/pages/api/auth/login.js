export default function handler(req, res){
  if(req.method !== 'POST') return res.status(405).end()
  const { username, password } = req.body
  // This is a stub. In production, validate against DB.
  if(username && password){
    return res.status(200).json({ ok:true })
  }
  res.status(400).json({ ok:false })
}
