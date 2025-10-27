export const config = {
  api: { bodyParser: false },
}
import formidable from 'formidable';
import fs from 'fs';

export default function handler(req, res){
  if(req.method !== 'POST') return res.status(405).end()
  const form = new formidable.IncomingForm();
  form.parse(req, (err, fields, files) => {
    if(err) return res.status(500).end();
    // In this stub we won't save file persistently. In production move to cloud storage.
    return res.status(200).json({ ok:true, filename: files.file?.originalFilename || null })
  })
}
