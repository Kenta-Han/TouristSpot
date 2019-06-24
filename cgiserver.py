#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## 直列処理
# import http.server
# print("Server Start")
# server_address = ("", 8000)
# handler_class = http.server.CGIHTTPRequestHandler
# server = http.server.HTTPServer(server_address, handler_class)
# server.serve_forever()


## 並列処理
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from http.server import CGIHTTPRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """マルチスレッド化した HTTPServer"""
    pass

print("Server Start 8000")
server_address = ("", 8000)
# マルチスレッド化した HTTP サーバを使う
httpd = ThreadedHTTPServer(server_address,CGIHTTPRequestHandler)
httpd.serve_forever()
