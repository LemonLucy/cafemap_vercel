import pg from 'pg';
import crypto from 'crypto';
const { Pool } = pg;

const pool = new Pool({
  host: '138.2.127.70',
  port: 5432,
  database: 'cafemap',
  user: 'cafemap',
  password: 'CafeMap2026Pass',
  ssl: false
});

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const { user_id, cafe_name, cafe_address, rating, review_text, image } = req.body;
    
    let image_url = null;
    
    // 이미지 처리는 나중에 (일단 텍스트만)
    if (image) {
      // TODO: 이미지를 Oracle 서버로 전송하거나 S3에 업로드
      console.log('Image upload not implemented yet');
    }
    
    const query = `
      INSERT INTO reviews (user_id, cafe_name, cafe_address, rating, review_text, image_url) 
      VALUES ($1, $2, $3, $4, $5, $6) 
      RETURNING id
    `;
    
    const result = await pool.query(query, [user_id, cafe_name, cafe_address || '', rating, review_text, image_url]);
    
    res.status(200).json({ success: true, review_id: result.rows[0].id });
  } catch (error) {
    console.error('Add review error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
}
