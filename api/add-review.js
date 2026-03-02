const { Client } = require('pg');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { user_id, cafe_name, rating, review_text, image } = req.body;
  
  const client = new Client({
    host: '138.2.127.70',
    port: 5432,
    database: 'cafemap',
    user: 'cafemap',
    password: 'CafeMap2026Pass'
  });
  
  try {
    await client.connect();
    
    // 이미지는 일단 null
    const result = await client.query(`
      INSERT INTO reviews (user_id, cafe_name, rating, review_text, image_url) 
      VALUES ($1, $2, $3, $4, $5) 
      RETURNING id
    `, [user_id, cafe_name, rating, review_text, null]);
    
    await client.end();
    
    res.status(200).json({ success: true, review_id: result.rows[0].id });
  } catch (error) {
    console.error('DB error:', error);
    res.status(500).json({ error: error.message });
  }
}
