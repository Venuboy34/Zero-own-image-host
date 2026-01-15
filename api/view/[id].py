from http.server import BaseHTTPRequestHandler
from pymongo import MongoClient
import os

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['image_hosting']
images_collection = db['images']

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path_parts = self.path.split('/')
            image_id = path_parts[-1].split('?')[0]
            
            image_doc = images_collection.find_one({'_id': image_id})
            
            if not image_doc:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Image not found</h1>')
                return
            
            host = self.headers.get('Host', 'your-api.vercel.app')
            protocol = 'https' if 'vercel.app' in host else 'http'
            image_url = f'{protocol}://{host}/api/image/{image_id}'
            
            # HTML page to view image
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{image_doc['filename']}</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        background: #1a1a1a;
                        color: #fff;
                        font-family: system-ui, -apple-system, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        min-height: 100vh;
                    }}
                    .container {{
                        max-width: 1200px;
                        width: 100%;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                    }}
                    .info {{
                        background: #2a2a2a;
                        padding: 20px;
                        border-radius: 8px;
                        margin-top: 20px;
                    }}
                    .info-item {{
                        margin: 10px 0;
                    }}
                    .url-box {{
                        background: #1a1a1a;
                        padding: 10px;
                        border-radius: 4px;
                        margin-top: 5px;
                        word-break: break-all;
                        cursor: pointer;
                    }}
                    .url-box:hover {{
                        background: #333;
                    }}
                    button {{
                        background: #0070f3;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        cursor: pointer;
                        margin: 5px;
                    }}
                    button:hover {{
                        background: #0051cc;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{image_doc['filename']}</h1>
                    <img src="{image_url}" alt="{image_doc['filename']}">
                    <div class="info">
                        <div class="info-item">
                            <strong>Direct URL:</strong>
                            <div class="url-box" onclick="copyToClipboard('{image_url}')" title="Click to copy">
                                {image_url}
                            </div>
                        </div>
                        <div class="info-item">
                            <strong>Size:</strong> {image_doc['size'] / 1024:.2f} KB
                        </div>
                        <div class="info-item">
                            <strong>Expires:</strong> {image_doc['expiresAt'].strftime('%Y-%m-%d %H:%M:%S')} UTC
                        </div>
                        <div class="info-item">
                            <button onclick="window.open('{image_url}', '_blank')">Open Image</button>
                            <button onclick="copyToClipboard('{image_url}')">Copy URL</button>
                            <button onclick="downloadImage()">Download</button>
                        </div>
                    </div>
                </div>
                <script>
                    function copyToClipboard(text) {{
                        navigator.clipboard.writeText(text).then(() => {{
                            alert('URL copied to clipboard!');
                        }});
                    }}
                    function downloadImage() {{
                        window.location.href = '{image_url}';
                    }}
                </script>
            </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<h1>Error: {str(e)}</h1>'.encode())
