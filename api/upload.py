from http.server import BaseHTTPRequestHandler
import json
import base64
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
import uuid

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['image_hosting']
images_collection = db['images']

# Create TTL index for auto-deletion after 30 days
images_collection.create_index("expiresAt", expireAfterSeconds=0)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            
            if 'image' not in data:
                self.send_error(400, 'No image data provided')
                return
            
            image_data = data['image']
            
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            try:
                decoded = base64.b64decode(image_data)
            except Exception:
                self.send_error(400, 'Invalid base64 image data')
                return
            
            # Check size (5MB limit)
            if len(decoded) > 5 * 1024 * 1024:
                self.send_error(400, 'Image size exceeds 5MB limit')
                return
            
            image_id = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(days=30)
            
            # Get host from headers
            host = self.headers.get('Host', 'your-api.vercel.app')
            protocol = 'https' if 'vercel.app' in host else 'http'
            
            image_doc = {
                '_id': image_id,
                'data': image_data,
                'filename': data.get('filename', 'image.png'),
                'mimetype': data.get('mimetype', 'image/png'),
                'size': len(decoded),
                'uploadedAt': datetime.utcnow(),
                'expiresAt': expires_at
            }
            
            images_collection.insert_one(image_doc)
            
            # Return direct image URLs
            response = {
                'success': True,
                'id': image_id,
                'url': f'{protocol}://{host}/api/image/{image_id}',
                'directUrl': f'{protocol}://{host}/api/image/{image_id}',
                'viewUrl': f'{protocol}://{host}/api/view/{image_id}',
                'deleteUrl': f'{protocol}://{host}/api/delete/{image_id}',
                'size': len(decoded),
                'filename': image_doc['filename'],
                'uploadedAt': datetime.utcnow().isoformat(),
                'expiresAt': expires_at.isoformat(),
                'expiresIn': '30 days'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
