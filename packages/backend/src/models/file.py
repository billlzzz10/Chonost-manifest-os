import json
from datetime import datetime

class FileModel:
    def __init__(self, db_connection):
        self.db = db_connection
        self.create_table()
    
    def create_table(self):
        """สร้างตารางไฟล์"""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                original_name TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT,
                user_id INTEGER NOT NULL,
                upload_type TEXT DEFAULT 'general',
                processed_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        

        
        self.db.commit()
    
    def create_file(self, file_data):
        """สร้างข้อมูลไฟล์ใหม่"""
        try:
            cursor = self.db.cursor()
            
            # แปลง processed_data เป็น JSON string
            processed_data_json = json.dumps(file_data.get('processed_data', {}))
            
            cursor.execute('''
                INSERT INTO files (
                    id, original_name, filename, file_path, file_type, 
                    file_size, mime_type, user_id, upload_type, processed_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_data['id'],
                file_data['original_name'],
                file_data['filename'],
                file_data['file_path'],
                file_data['file_type'],
                file_data['file_size'],
                file_data['mime_type'],
                file_data['user_id'],
                file_data['upload_type'],
                processed_data_json
            ))
            

            
            self.db.commit()
            return {'success': True, 'data': file_data}
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}
    
    def get_file_by_id(self, file_id):
        """ดึงข้อมูลไฟล์จาก ID"""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT id, original_name, filename, file_path, file_type, 
                   file_size, mime_type, user_id, upload_type, processed_data,
                   created_at, updated_at
            FROM files 
            WHERE id = ?
        ''', (file_id,))
        
        row = cursor.fetchone()
        if row:
            file_data = {
                'id': row[0],
                'original_name': row[1],
                'filename': row[2],
                'file_path': row[3],
                'file_type': row[4],
                'file_size': row[5],
                'mime_type': row[6],
                'user_id': row[7],
                'upload_type': row[8],
                'created_at': row[10],
                'updated_at': row[11]
            }
            
            # แปลง processed_data จาก JSON
            try:
                file_data['processed_data'] = json.loads(row[9]) if row[9] else {}
            except:
                file_data['processed_data'] = {}
            
            return file_data
        
        return None
    
    def get_user_files(self, user_id, file_type=None, page=1, per_page=20):
        """ดึงรายการไฟล์ของผู้ใช้"""
        try:
            cursor = self.db.cursor()
            
            # สร้าง query
            base_query = '''
                SELECT id, original_name, file_type, file_size, mime_type, 
                       upload_type, created_at
                FROM files 
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if file_type:
                base_query += ' AND file_type = ?'
                params.append(file_type)
            
            # นับจำนวนทั้งหมด
            count_query = base_query.replace('SELECT id, original_name, file_type, file_size, mime_type, upload_type, created_at', 'SELECT COUNT(*)')
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # เพิ่ม pagination
            base_query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([per_page, (page - 1) * per_page])
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            files = []
            for row in rows:
                files.append({
                    'id': row[0],
                    'original_name': row[1],
                    'file_type': row[2],
                    'file_size': row[3],
                    'mime_type': row[4],
                    'upload_type': row[5],
                    'created_at': row[6],
                    'url': f'/api/files/{row[0]}'
                })
            
            return {
                'success': True,
                'data': {
                    'files': files,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page
                    }
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}
    
    def delete_file(self, file_id):
        """ลบไฟล์"""
        try:
            cursor = self.db.cursor()
            

            
            # ลบไฟล์
            cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
            
            if cursor.rowcount > 0:
                self.db.commit()
                return {'success': True, 'message': 'ลบไฟล์สำเร็จ'}
            else:
                return {'success': False, 'message': 'ไม่พบไฟล์ที่ต้องการลบ'}
                
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}
    

    

    

    


