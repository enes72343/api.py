from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Veritabanını kur
def setup_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  license_key TEXT UNIQUE,
                  bot_name TEXT,
                  status TEXT,
                  sunucu_id TEXT,
                  sunucu_adi TEXT,
                  last_sync TEXT)''')
    conn.commit()
    conn.close()

setup_db()

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'API çalışıyor', 'message': 'ViolentLua Lisans API'})

@app.route('/api', methods=['POST'])
def api():
    try:
        data = request.json
        action = data.get('action')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Lisans güncelle (botlardan gelir)
        if action == 'update_license':
            c.execute('''INSERT OR REPLACE INTO licenses 
                         (license_key, bot_name, status, sunucu_id, sunucu_adi, last_sync) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (data.get('license_key'),
                       data.get('bot_name', 'Bilinmiyor'),
                       data.get('status', 'inactive'),
                       data.get('sunucu_id', ''),
                       data.get('sunucu_adi', ''),
                       datetime.now().isoformat()))
            conn.commit()
            return jsonify({'success': True})
        
        # Tüm lisansları getir (admin panel için)
        if action == 'get_all':
            c.execute("SELECT * FROM licenses ORDER BY last_sync DESC")
            rows = c.fetchall()
            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'license_key': row[1],
                    'bot_name': row[2],
                    'status': row[3],
                    'sunucu_id': row[4],
                    'sunucu_adi': row[5],
                    'last_sync': row[6]
                })
            return jsonify({'success': True, 'data': result})
        
        # Lisans sil
        if action == 'delete_license':
            c.execute("DELETE FROM licenses WHERE license_key = ?", (data.get('license_key'),))
            conn.commit()
            return jsonify({'success': True})
        
        conn.close()
        return jsonify({'success': False, 'error': 'Bilinmeyen action'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
