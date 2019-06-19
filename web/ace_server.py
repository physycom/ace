#! /usr/bin/env python3

from http.server import BaseHTTPRequestHandler
import os
import json
import re
from matplotlib import cm

acemapfile = ''
italy_feat = {
  'type': 'Feature',
  'properties': {
    'code' : 'Italy',
    'color': 'rgb(255, 0, 0)',
    'time_cnt': [
      0.1,
      0.5,
      1.0,
      0.75,
      0.1
    ]
  },
  'geometry': {
    'type': 'Point',
    'coordinates': [12.833333333333334, 42.8333333] # italy center
  }
}
default_times = [
  '20190101-0000',
  '20190101-0015',
  '20190101-0030',
  '20190101-0045',
  '20190101-0100'
]

class Server(BaseHTTPRequestHandler):
  def __init__(self, *args):
    with open(acemapfile) as f:
      self.istat = json.load(f)
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

  def extract_geofeature_9digit(self, features, tag, color):
    reg = str(int(tag[0:3]))
    prov = str(int(tag[3:6]))
    com = str(int(tag[6:9]))
    name = ''
    c = [0,0]
    try:
      comobj = self.istat['reg'][reg]['prov'][prov]['com'][com]
      empty_feat = {
        'type': 'Feature',
        'properties': {
          'code' : '',
          'color': color
        },
        'geometry': {
          'type': 'Point',
          'coordinates': []
        }
      }
      empty_feat['properties']['code'] = comobj['name']
      if comobj['centroid'] == [0,0]:
        print('Null geodata for : ' + reg + '|' + prov + '|' + com + ' ' + comobj['name'])
        return
      empty_feat['geometry']['coordinates'] = comobj['centroid']

      if 'time_count' in comobj:
        empty_feat['properties']['time_cnt'] = comobj['time_count']
      features.append(empty_feat)
    except:
      print('No acemap match for : ' + reg + '|' + prov + '|' + com)

  def extract_geofeature_6digit(self, features, tag, color):
    reg = str(int(tag[0:3]))
    prov = str(int(tag[3:6]))
    for com in self.istat['reg'][reg]['prov'][prov]['com'].keys():
      self.extract_geofeature_9digit(features, tag + '{:0>3}'.format(com), color)

  def extract_geofeature_3digit(self, features, tag, color):
    reg = str(int(tag))
    for prov in self.istat['reg'][reg]['prov'].keys():
      self.extract_geofeature_6digit(features, tag + '{:0>3}'.format(prov), color)

  def extract_geofeature_italy(self, features, tag, color):
    for reg in self.istat['reg'].keys():
      self.extract_geofeature_3digit(features, '{:0>3}'.format(reg), color)

  def handle_http(self):
    if self.path.endswith('.html'):
      try:
        htmlfile = self.path.split('/')[-1]
        status, content_type, response_content, size = self.serve_html(htmlfile)
      except:
        status, content_type, response_content, size = self.serve_404()
    elif self.path == '/':
      status, content_type, response_content, size = self.serve_html('index.html')
    elif self.path.startswith('/anim'):
      status, content_type, response_content, size = self.serve_html('acemap_animation.html')
    elif self.path.startswith('/mob'):
      status, content_type, response_content, size = self.serve_html('acemap_mobility.html')
    elif self.path.startswith('/view'):
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

      for i,p in enumerate(params):
        scale = 0 if len(params) == 1 else ( i * 255 ) // (len(params)-1)
        color = 'rgba(' + ','.join([ str(int(c*255)) for c in cm.jet(scale)]) + ')'
        if len(p) == 0:
          continue
        elif re.search(r'^\d{3}(?!\d)', p):
          self.extract_geofeature_3digit(geojson['features'], p, color)
        elif re.search(r'^\d{6}(?!\d)', p):
          self.extract_geofeature_6digit(geojson['features'], p, color)
        elif re.search(r'^\d{9}(?!\d)', p):
          self.extract_geofeature_9digit(geojson['features'], p, color)
        elif p == 'italy':
          self.extract_geofeature_italy(geojson['features'], p, color)
        else:
          print('No query match : ' + p)

      # sanity checks and various init
      if 'times' in self.istat:
        geojson['times'] = self.istat['times']

      if len(geojson['features']) == 0:
        print('pusho italy')
        geojson['features'].append(italy_feat)
        geojson['times'] = default_times

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
  parser.add_argument('-m', '--acemap', help='acemap json file', required=True)
  args = parser.parse_args()
  acemapfile = args.acemap

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
