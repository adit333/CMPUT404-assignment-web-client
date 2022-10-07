#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
from typing import Tuple
from urllib import request
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self) -> str:
        return f'HTTPResponse: {self.code}\n{self.body}'


class HTTPClient(object):
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)

        request = f'GET {path} HTTP/1.1\r\n'
        request += f'Host: {host}\r\n'
        request += 'Accept: */*\r\n'
        request += 'Connection: close\r\n'
        request += '\r\n'

        self.connect(host, port)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.parse_url(url)

        body = ''
        if args:
            body = urllib.parse.urlencode(args)

        request = f'POST {path} HTTP/1.1\r\n'
        request += f'Host: {host}\r\n'
        request += "Accept: */*\r\n"
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        request += f'Content-Length: {len(body)}\r\n'
        request += 'Connection: close\r\n'

        request += '\r\n'
        request += body
    
        self.connect(host, port)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def parse_url(self, url: str) -> Tuple[str, int, str]:
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or 80
        path = parsed_url.path or '/'
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, response):
        header_first_line = response.split('\r\n')[0]
        return int(header_first_line.split(' ')[1])

    def get_headers(self, response):
        response_lines = response.split('\r\n')
        headers = []
        for line in response_lines[1:]:
            if line == '':
                break
            headers.append(line)
        return headers

    def get_body(self, response):
        body = response.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        # return sock.recv(4096).decode('utf-8')
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
