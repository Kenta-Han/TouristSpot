import http.server

print("Start Server http://127.0.0.1:8000/~")
server_address = ("", 8000)
handler_class = http.server.CGIHTTPRequestHandler
server = http.server.HTTPServer(server_address, handler_class)
server.serve_forever()
