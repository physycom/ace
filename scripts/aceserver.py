#! /usr/bin/env python3

from http.server import BaseHTTPRequestHandler
import os
import json

class Server(BaseHTTPRequestHandler):
  def __init__(self, *args):
    with open('acemap.json') as f:
      self.acedb = json.load(f)
    BaseHTTPRequestHandler.__init__(self, *args)

  def do_HEAD(self):
    return

  def do_POST(self):
    return

  def do_GET(self):
    self.respond()

  def handle_http(self):
    if self.path == "/":
      status = 200
      content_type = "text/plain"
      response_content = "Site under construction"
      response_content = bytes(response_content, "UTF-8")
      size = len(response_content)
    if self.path.startswith("/q"):
      query = self.path.split('?')[1:]
      status = 200
      content_type = "text/plain"
      response_content = "Query : " + '-'.join(query)
      response_content = bytes(response_content, "UTF-8")
      size = len(response_content)
    elif self.path.startswith('/json'):
      status = 200
      content_type = 'application/json'
      geojson = {
        'type': 'FeatureCollection',
        'features': []
      }
      empty_feat = {
        'type': 'Feature',
        'properties': {
          'code' : 'Italy',
          'color': 'rgb(255, 0, 0)'
        },
        'geometry': {
          'type': 'MultiPoint',
          'coordinates': [
            [12.833333333333334, 42.8333333] # italy center
          ]
        }
      }

      params = self.path.split('?')[1:]
      if len(params) == 0:
        geojson['features'].append(empty_feat)

      response_content = json.dumps(geojson)
      response_content = bytes(response_content, "UTF-8")
      size = len(response_content)
    else:
      status = 404
      content_type = "text/plain"
      response_content = "404 Url not found."
      response_content = bytes(response_content, "UTF-8")
      size = len(response_content)

    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.send_header('Content-length', size)
    self.end_headers()
    return response_content

  def respond(self):
    content = self.handle_http()
    self.wfile.write(content)


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--server-address', help='http server address', default='localhost')
parser.add_argument('-p', '--server-port', help='http server port', default=9999, type=int)
args = parser.parse_args()

import time
from http.server import HTTPServer

HOST_NAME = args.server_address
PORT_NUMBER = args.server_port

if __name__ == '__main__':
  httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
  print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    pass
  httpd.server_close()
print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))




