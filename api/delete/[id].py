from http.server import BaseHTTPRequestHandler
from pymongo import MongoClient
import os
import json

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['image_hosting']
images_collection = db['images']

class handler(BaseHTTPRequestHandler):
    def do_DELETE(self):
        try:
            path_parts = self.path.split('/')
            image_id = path_parts[-1].split('?')[0]
            
            result = images_collection.delete_one({'_id': image_id})
            
            if result.deleted_count == 0:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Image not found"}')
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Image deleted'}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
