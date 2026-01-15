from http.server import BaseHTTPRequestHandler
import base64
from pymongo import MongoClient
import os

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['image_hosting']
images_collection = db['images']

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract image ID from path
            path_parts = self.path.split('/')
            image_id = path_parts[-1].split('?')[0]
            
            # Find image in database
            image_doc = images_collection.find_one({'_id': image_id})
            
            if not image_doc:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Image not found"}')
                return
            
            # Decode base64 image
            image_data = base64.b64decode(image_doc['data'])
            
            # Send image with proper headers
            self.send_response(200)
            self.send_header('Content-type', image_doc['mimetype'])
            self.send_header('Content-Length', str(len(image_data)))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(image_data)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
