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
      { 'datetime' : '20190101-0000', 'cnt' : 0.1 },
      { 'datetime' : '20190101-0015', 'cnt' : 0.5  },
      { 'datetime' : '20190101-0030', 'cnt' : 1.0  },
      { 'datetime' : '20190101-0045', 'cnt' : 0.75 },
      { 'datetime' : '20190101-0100', 'cnt' : 0.1  }
    ]
  },
  'geometry': {
    'type': 'Point',
    'coordinates': [12.833333333333334, 42.8333333] # italy center
  }
}

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
      name = self.istat['reg'][reg]['prov'][prov]['com'][com]['name']
      c = self.istat['reg'][reg]['prov'][prov]['com'][com]['centroid']
      empty_feat = {
        'type': 'Feature',
        'properties': {
          'code' : '',
          'color': 'rgb(255, 0, 0)'
        },
        'geometry': {
          'type': 'Point',
          'coordinates': []
        }
      }
      empty_feat['properties']['code'] = name
      empty_feat['geometry']['coordinates'] = c
      features.append(empty_feat)
    except:
      print('No acemap match for : ' + reg + '|' + prov + '|' + com)

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
      geojson = {
        'type': 'FeatureCollection',
        'features': [],
        'times': [
          '20190101-0000',
          '20190101-0015',
          '20190101-0030',
          '20190101-0045',
          '20190101-0100'
        ]
      }

      params = self.path.split('?')
      if len(params) == 2:
        params = params[1].split('&')
      else:
        params = ['']

      for i,p in enumerate(params):
        scale = 0 if len(params) == 1 else ( i * 255 ) // (len(params)-1)
        color = cm.jet( scale )
        color = 'rgba(' + ','.join([ str(int(c*255)) for c in color]) + ')'
        if len(p) == 0:
          continue
        elif re.search(r'^\d{3}(?!\d)', p):
          reg = str(int(p))
          for provid, prov in self.istat['reg'][reg]['prov'].items():
            try:
              for k,v in prov['com'].items():
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
                empty_feat['properties']['code'] = v['name']
                if v['centroid'] == [0,0]:
                  print('Null geodata for ' + v['name'] + '(' + reg + '|' + prov + '|' + k + ')')
                  continue
                empty_feat['geometry']['coordinates'] = v['centroid']
                geojson['features'].append(empty_feat)
            except:
              print('No geodata for ' + reg + '|' + provid)
              continue
        elif re.search(r'^\d{6}(?!\d)', p):
          reg = str(int(p[0:3]))
          prov = str(int(p[3:6]))
          try:
            for k,v in self.istat['reg'][reg]['prov'][prov]['com'].items():
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
              empty_feat['properties']['code'] = v['name']
              if v['centroid'] == [0,0]:
                print('Null geodata for ' + v['name'] + '(' + reg + '|' + prov + '|' + k + ')')
                continue
              empty_feat['geometry']['coordinates'] = v['centroid']
              geojson['features'].append(empty_feat)
          except:
            print('No match for ' + reg + '|' + prov)
            continue
        elif re.search(r'^\d{9}(?!\d)', p):
          self.extract_geofeature_9digit(geojson['features'], p, color)
        else:
          print('No query match : ' + p)

      if len(geojson['features']) == 0:
        geojson['features'].append(italy_feat)

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
