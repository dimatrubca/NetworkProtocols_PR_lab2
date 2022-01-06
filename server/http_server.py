from email import message
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import smtp

HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8000

def create_http_server():
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print('Server Up')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print('Server Down')

class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        filename = query_components["filename"]
        email = query_components["email"]

        self.respond(filename, email)
        
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        field_data = self.rfile.read(length)
        fields = urlparse.parse_qs(field_data)
        filename = fields["filename"]
        email = fields["email"]

        self.respond(filename, email)

    def handle_http(self, status, content_type):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

        message = 'Success' if status == 200 else 'Error'
        return bytes(message, 'UTF-8')


    
    def respond(self, filename, email):
        if filename is None or email is None:
            content = self.handle_http(400, 'text/html')
        else:
            content = self.handle_http(200, 'text/html') # todo: change to json

            with open('data/' + filename, 'r') as f:
                json_file = json.loads(f.read())
                smtp.send_email(email, json_file, filename)

        self.wfile.write(content)

if __name__ == '__main__':
    create_http_server()