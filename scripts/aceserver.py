#! /usr/bin/env python3

from http.server import BaseHTTPRequestHandler
import os
import json
import re
from matplotlib import cm

acemapfile = ''

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

  def handle_http(self):
    if self.path == '/':
      status = 200
      content_type = 'text/html; charset=utf-8'
      response_content = 'Site under construction'
      response_content = bytes(response_content, 'UTF-8')
      size = len(response_content)
    elif self.path.startswith('/anim'):
      f = open(os.path.dirname(os.path.realpath(__file__)) + '/html/acemap_animation.html')
      status = 200
      content_type = 'text/html; charset=ISO-8859-1'
      response_content = f.read()
      response_content = bytes(response_content, 'UTF-8')
      size = len(response_content)
    elif self.path.startswith('/mob'):
      f = open(os.path.dirname(os.path.realpath(__file__)) + '/html/acemap_mobility.html')
      status = 200
      content_type = 'text/html; charset=ISO-8859-1'
      response_content = f.read()
      response_content = bytes(response_content, 'UTF-8')
      size = len(response_content)
    elif self.path.startswith('/view'):
      f = open(os.path.dirname(os.path.realpath(__file__)) + '/html/acemap_view.html')
      status = 200
      content_type = 'text/html; charset=ISO-8859-1'
      response_content = f.read()
      response_content = bytes(response_content, 'UTF-8')
      size = len(response_content)
    elif self.path.startswith('/json'):
      status = 200
      content_type = 'application/json; charset=ISO-8859-1'
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

      params = self.path.split('?')
      if len(params) == 2:
        params = params[1].split('&')
      else:
        params = ['']

      for i,p in enumerate(params):
        scale = 0 if len(params) == 1 else ( i * 255 ) // (len(params)-1)
        color = cm.jet( scale )
        color = 'rgba(' + ','.join([ str(int(c*255)) for c in color]) + ')'
#        print(color)
        if len(p) == 0:
#          print('Match 0 digit : -' + p + '-')
          continue
        elif re.search(r'^\d{3}(?!\d)', p):
#          print('Match 3 digit : ' + p)
          reg = str(int(p))
          for provid, prov in self.istat[reg]['prov'].items():
            try:
#              print(provid, prov['name'])
              for k,v in prov['com'].items():
#                print('--- ',k,v['name'])
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
                  print('No geodata for ' + v['name'] + '(' + reg + '|' + prov + '|' + k + ')')
                  continue
                empty_feat['geometry']['coordinates'] = v['centroid']
                geojson['features'].append(empty_feat)
            except:
              print('No geodata for ' + reg + '|' + provid)
              continue
        elif re.search(r'^\d{6}(?!\d)', p):
#          print('Match 6 digit : ' + p)
          reg = str(int(p[0:3]))
          prov = str(int(p[3:6]))
          try:
            for k,v in self.istat[reg]['prov'][prov]['com'].items():
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
                print('No geodata for ' + v['name'] + '(' + reg + '|' + prov + '|' + k + ')')
                continue
              empty_feat['geometry']['coordinates'] = v['centroid']
              geojson['features'].append(empty_feat)
          except:
            print('No geodata for ' + reg + '|' + prov)
            continue
        elif re.search(r'^\d{9}(?!\d)', p):
#          print('Match 9 digit : ' + p)
          reg = str(int(p[0:3]))
          prov = str(int(p[3:6]))
          com = str(int(p[6:9]))
          name = ''
          c = [0,0]
          try:
            name = self.istat[reg]['prov'][prov]['com'][com]['name']
            c = self.istat[reg]['prov'][prov]['com'][com]['centroid']
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
            geojson['features'].append(empty_feat)
          except:
            print('No acemap match for : ' + reg + '|' + prov + '|' + com)
            continue
#          print('Match for ' + p + ' : ' + name + ' ' + str(c[0]) + ' ' + str(c[1]))
        else:
          print('No query match : ' + p)

      if len(geojson['features']) == 0:
        geojson['features'].append(italy_feat)

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
parser.add_argument('-m', '--acemap', help='acemap json file', required=True)
args = parser.parse_args()
acemapfile = args.acemap

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




