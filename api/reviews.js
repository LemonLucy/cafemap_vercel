export default async function handler(req, res) {
  const { cafe_name } = req.query;
  
  if (!cafe_name) {
    return res.status(400).json({ error: 'cafe_name required' });
  }
  
  try {
    const response = await fetch(`http://138.2.127.70:8000/api/reviews/cafe/${encodeURIComponent(cafe_name)}`);
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('Reviews proxy error:', error);
    res.status(500).json({ error: error.message });
  }
}
