#! /usr/bin/env python3

from http.server import BaseHTTPRequestHandler
import os
import json
import re
from matplotlib import cm

acedata = ''

class Server(BaseHTTPRequestHandler):
  def __init__(self, *args):
    BaseHTTPRequestHandler.__init__(self, *args)

  def do_HEAD(self):
    return

  def do_POST(self):
    return

  def do_GET(self):
    self.respond()

  def serve_html(self, filename):
    f = open(os.path.dirname(os.path.realpath(__file__)) + '/html/' + filename)
    status = 200
    content_type = 'text/html; charset=ISO-8859-1'
    response_content = f.read()
    response_content = bytes(response_content, 'UTF-8')
    size = len(response_content)
    return status, content_type, response_content, size

  def serve_404(self):
    status = 404
    content_type = "text/plain"
    response_content = "404 Url not found."
    response_content = bytes(response_content, "UTF-8")
    size = len(response_content)
    return status, content_type, response_content, size

  def serve_json(self, geojson):
    status = 200
    content_type = 'application/json; charset=ISO-8859-1'
    response_content = json.dumps(geojson)
    response_content = bytes(response_content, "UTF-8")
    size = len(response_content)
    return status, content_type, response_content, size

  def handle_http(self):
    if self.path.endswith('.html'):
      try:
        htmlfile = self.path.split('/')[-1]
        status, content_type, response_content, size = self.serve_html(htmlfile)
      except:
        status, content_type, response_content, size = self.serve_404()
    elif self.path == '/':
      status, content_type, response_content, size = self.serve_html('index.html')
    elif self.path.startswith('/shape'):
      status, content_type, response_content, size = self.serve_html('acemap_view.html')
    elif self.path.startswith('/json'):
      params = self.path.split('?')
      if len(params) == 2:
        params = params[1].split('&')
      else:
        params = ['']

      geojson = {
        'type': 'FeatureCollection',
        'features': [],
      }

      for p in params:
        acelist = [ a for a in aced.keys() if a.startswith(p) ]
        for a in acelist:
          feat = {
            'type': 'Feature',
            'properties': {
              'code' : a,
              'color': 'rgba(255,0,0,0.3)'
            },
            'geometry': aced[a]['geometry']
          }
          geojson['features'].append(feat)
        if len(acelist) == 0:
          print('ACETAG {} not found, skipping.'.format(p))
      status, content_type, response_content, size = self.serve_json(geojson)

    else:
      status, content_type, response_content, size = self.serve_404()

    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.send_header('Content-length', size)
    self.end_headers()
    return response_content

  def respond(self):
    content = self.handle_http()
    self.wfile.write(content)


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-a', '--server-address', help='http server address', default='localhost')
  parser.add_argument('-p', '--server-port', help='http server port', default=9999, type=int)
  parser.add_argument('-d', '--ace-data', help='ISTAT geojson region file', required=True)
  args = parser.parse_args()
  acedata = args.ace_data

  with open(acedata) as f:
    ace = json.load(f)
  print(ace.keys())
  print(len(ace['features']))

  aced = {}
  for feat in ace['features']:
    reg = '{:03.0f}'.format(feat['properties']['COD_REG'])
    procom = int(feat['properties']['PRO_COM'])
    pro = '{:03d}'.format(procom // 1000)
    com = '{:03d}'.format(procom - (procom // 1000) * 1000)
    sezfull = feat['properties']['SEZ2011']
    sezfull = int(sezfull - int(sezfull / 1e7)*1e7)
    sez = '{:03.0f}'.format(sezfull // 1000)
    sezace = '{:03.0f}'.format(sezfull - (sezfull // 1000) * 1000)
    acetag = '|'.join([reg, pro, com, sez, sezace])
    #print(acetag)
    if acetag in aced:
      print('ACETAG {} duplicated, skipping'.format(acetag))
      continue
    aced[acetag] = {
      'geometry' : feat['geometry']
    }

  print('ACE parsed : {}'.format(len(aced)))
  acelist = acedata[:acedata.rfind('.')] + '.acelist'
  with open(acelist, 'w') as f:
    for a in sorted(aced.keys()):
      f.write('{}\n'.format(a))
  print('ACE list file : {}'.format(acelist))

  import time
  from http.server import HTTPServer

  HOST_NAME = args.server_address
  PORT_NUMBER = args.server_port

  httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
  print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))
