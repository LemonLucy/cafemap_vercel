export default async function handler(req, res) {
  const { cafe_name, user_id } = req.query;
  
  let url = 'http://138.2.127.70:8001/api/reviews';
  const params = new URLSearchParams();
  if (cafe_name) params.append('cafe_name', cafe_name);
  if (user_id) params.append('user_id', user_id);
  if (params.toString()) url += '?' + params.toString();
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
}
