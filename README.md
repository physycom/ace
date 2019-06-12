# ace

[![Build Status](https://travis-ci.com/physycom/ace.svg?branch=master)](https://travis-ci.com/physycom/ace)

[![Build status](https://ci.appveyor.com/api/projects/status/kcl6000vv11rwxca?svg=true)](https://ci.appveyor.com/project/cenit/ace)

ACE : Aree di Censimento
SCE : Sezione di Censimento

Data available at
https://www.istat.it/it/archivio/104317
Run `ace` on every kmz and cat the result after `sort` and `uniq`


### C++ Tools

- `remap`
  . input: istat kmz file
  . output: (shell) csv with format `ace_id,lat,lon`

- `animate`
  . input: ?
  . output: ?

- `remap`
  . input: ?
  . output: ?


### Python Tools

- 'aceserver.py'
Local http server to fetch for geojson data. (WIP)

- 'test.html'
Sample web page to visualize geodata. Bypass CORS policy with
  . MacOS : `open -a Google\ Chrome --args --disable-web-security --user-data-dir="/somedir"`
