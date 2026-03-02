const { Client } = require('pg');

export default async function handler(req, res) {
  const { cafe_name } = req.query;
  
  if (!cafe_name) {
    return res.status(400).json({ error: 'cafe_name required' });
  }
  
  const client = new Client({
    host: '138.2.127.70',
    port: 5432,
    database: 'cafemap',
    user: 'cafemap',
    password: 'CafeMap2026Pass'
  });
  
  try {
    await client.connect();
    
    const result = await client.query(`
      SELECT r.id, r.user_id, u.nickname, r.cafe_name, r.rating, r.review_text as content, r.image_url, r.created_at 
      FROM reviews r 
      JOIN users u ON r.user_id = u.id 
      WHERE r.cafe_name = $1 
      ORDER BY r.created_at DESC
    `, [cafe_name]);
    
    await client.end();
    
    res.status(200).json(result.rows);
  } catch (error) {
    console.error('DB error:', error);
    res.status(500).json({ error: error.message });
  }
}
