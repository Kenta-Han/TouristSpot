#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb

print("<!DOCTYPE html>")
print("<head>")
print("Content-type:text/html; charset=UTF-8\r\n")
print("<link href='/data/stylesheet.css' rel='stylesheet' type='text/css' />")
print("<title>観光スポット</title>")
print("</head>")

print("<body>")

print("<div class='box1'>")
print("<header>")
print("<h1>観光スポット</h1>")
print("</header><br/>")

print("<form action='select_type.py' method='post'  style='text-align:center;'>")
print("<input type='submit' value='提案手法' class='button1'/>")
print("</form>")

print("<form action='only_type1.py' method='post'  style='text-align:center;'>")
print("<input type='submit' value='ジャンル' class='button1'/>")
print("</form>")


print("</div>")
print("</body></html>")
