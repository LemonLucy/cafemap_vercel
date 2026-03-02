export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const response = await fetch('http://138.2.127.70:8000/api/blog-search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
      timeout: 10000
    });
    
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('Blog search error:', error.message);
    res.status(500).json({ error: error.message });
  }
}
