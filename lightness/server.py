from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import json
import subprocess

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'

        self.path = "../htdocs" + self.path

        ext = self.path[self.path.rfind(".")+1:].lower()

        is_bytes = False
        if ext == 'ico':
            is_bytes = True
        elif ext == 'woff':
            is_bytes = True
        elif ext == 'woff2':
            is_bytes = True
        elif ext == 'ttf':
            is_bytes = True

        try:
            if is_bytes:
                file_to_open = open(self.path[1:], 'rb').read()
            else:
                file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except Exception as e:
            print(e)
            file_to_open = "File not found"
            self.send_response(404)

        self.end_headers()

        if is_bytes:
            self.wfile.write(file_to_open)
        else:
            self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()

        post_data = json.loads(body.decode("utf-8"))
        url = post_data['url']
        is_color = post_data['color']

        response_details = {}
        response_details['url'] = url
        response_details['is_color'] = is_color

        # do something with the data
        command = ["python3", "/home/pi/lightness/video.py"]
        command.append("--url")
        command.append(url)

        if (is_color):
            command.append("--color")

        subprocess.Popen(command)

        response_details['success'] = True
        response.write(bytes(json.dumps(response_details), 'utf-8'))
        self.wfile.write(response.getvalue())

httpd = HTTPServer(('0.0.0.0', 80), SimpleHTTPRequestHandler)
httpd.serve_forever()
