from flask import Flask, request, jsonify
import pymysql
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'API çalışıyor', 'message': 'ViolentLua Lisans API'})

@app.route('/api', methods=['POST'])
def api():
    try:
        data = request.json
        action = data.get('action')
        
        # MySQL bağlantısı
        conn = pymysql.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME'),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        if action == 'update_license':
            sql = """INSERT INTO licenses (license_key, status, sunucu_id, sunucu_adi, last_sync) 
                     VALUES (%s, %s, %s, %s, %s) 
                     ON DUPLICATE KEY UPDATE 
                     status = VALUES(status), 
                     sunucu_id = VALUES(sunucu_id), 
                     sunucu_adi = VALUES(sunucu_adi), 
                     last_sync = VALUES(last_sync)"""
            
            cursor.execute(sql, (
                data.get('license_key'),
                data.get('status'),
                data.get('sunucu_id', ''),
                data.get('sunucu_adi', ''),
                datetime.now()
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True})
            
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': 'Bilinmeyen action'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
