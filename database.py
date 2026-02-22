import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('venue.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cafes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  address TEXT,
                  phone TEXT,
                  x TEXT,
                  y TEXT,
                  keywords TEXT,
                  blog_count INTEGER,
                  updated_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_cafes(cafes):
    conn = sqlite3.connect('venue.db')
    c = conn.cursor()
    c.execute('DELETE FROM cafes')
    for cafe in cafes:
        x = str(cafe.get('longitude', cafe.get('x', '')))
        y = str(cafe.get('latitude', cafe.get('y', '')))
        c.execute('''INSERT INTO cafes (name, address, phone, x, y, keywords, blog_count, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (cafe['name'], cafe['address'], cafe['phone'], x, y,
                   json.dumps(cafe['keywords']), cafe.get('blog_count', 0), datetime.now()))
    conn.commit()
    conn.close()

def get_cafes():
    conn = sqlite3.connect('venue.db')
    c = conn.cursor()
    c.execute('SELECT name, address, phone, x, y, keywords, blog_count FROM cafes')
    rows = c.fetchall()
    conn.close()
    return [{"name": r[0], "address": r[1], "phone": r[2], 
             "latitude": float(r[4]), "longitude": float(r[3]),
             "keywords": json.loads(r[5]), "blog_count": r[6],
             "category": "relax"} for r in rows]
