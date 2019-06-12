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
Located in folder `scripts`

- `acemap_generator.py`
Create an *acemap* of italian _comuni_ without geodata.
 . input: `Elenco-comuni-italiani.csv` available here https://www.istat.it/it/archivio/6789
 . output: `acemap-empty.json` which is a nested json of format
`
acemap['regione_id']['prov']['provincia_id']['com']['comune_id'] = {
  'name'      : 'name'  // italian denomination of _comune_
  'centroid'  : [0,0]   // [lon, lat] of _comune_ centroid
  'sez_count' : 0       // number of SCE associated to given _comune_
}
`

- `acemap_geoupdate.py`
Update geodata on an *acemap* of italian _comuni_ populating fields: `centroid` and `sez_count`.
 . input: `acemap.json` properly formatted
 . input: `region_shapefile.geojson` as available here https://www.istat.it/it/archivio/104317
 . output: `acemap_RXX.geojson` where `RXX` is the _regione_ shapefile tag (e.g. `R01` is for _Piemonte_)

- `aceserver.py`
Local http server which provides *acemap* json data through GET requests.
 . input: `acemap.json` as produced by previous tools
 . output: through html GET request at url `http://address:port/json?query` where `query` is a string formatted as
  - `reg` returns
  - `regprov` returns
  - `regprovcom` returns

- `acemap_view.html`
Sample web page to visualize geodata. Bypass CORS policy with `Google Chrome` by:
  . MacOS : `open -a Google\ Chrome --args --disable-web-security --user-data-dir="/somedir"`

### Documentazione
Details of ISTAT databases
https://www.istat.it/it/files/2013/11/2015.04.28-Descrizione-dati-Pubblicazione.pdf
