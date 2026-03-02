export default async function handler(req, res) {
  const { cafe_name, user_id } = req.query;
  
  let url = 'http://138.2.127.70:8000/api/reviews/cafe';
  if (cafe_name) {
    url += '/' + encodeURIComponent(cafe_name);
  } else if (user_id) {
    url += '?user_id=' + user_id;
  }
  
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
}
