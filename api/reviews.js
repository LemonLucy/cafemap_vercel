export default async function handler(req, res) {
  const { cafe_name, user_id } = req.query;
  
  let url = 'http://138.2.127.70:8001/api/reviews';
  const params = new URLSearchParams();
  if (cafe_name) params.append('cafe_name', cafe_name);
  if (user_id) params.append('user_id', user_id);
  if (params.toString()) url += '?' + params.toString();
  
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
