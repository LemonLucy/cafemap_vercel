export default async function handler(req, res) {
  const { path } = req.query;
  
  if (!path) {
    return res.status(400).send('Missing path');
  }
  
  try {
    const response = await fetch(`http://138.2.127.70:8001/uploads/${path}`);
    const buffer = await response.arrayBuffer();
    
    res.setHeader('Content-Type', response.headers.get('content-type') || 'image/jpeg');
    res.setHeader('Cache-Control', 'public, max-age=31536000');
    res.send(Buffer.from(buffer));
  } catch (error) {
    res.status(404).send('Image not found');
  }
}
