/* Copyright 2018 - Stefano Sinigardi */

/***************************************************************************
This file is part of ace.

ace is free software : you can redistribute it and / or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ace is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ace. If not, see <http://www.gnu.org/licenses/>.
***************************************************************************/
#include <string>

static const std::string html_header =
R"(
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Leaflet Heatmap Layer Plugin</title>
    <style>
      body, html { margin:0; padding:0; height:100%;}
      body { font-family:sans-serif; }
      body * { font-weight:200;}
      h1 { position:absolute; background:white; padding:10px;}
      #map { height:100%; }
      .leaflet-container {
        background: rgba(0,0,0,.8) !important;
      }
      h1 { position:absolute; background:black; color:white; padding:10px; font-weight:200; z-index:10000;}
      #all-examples-info { position:absolute; background:white; font-size:16px; padding:20px; top:100px; width:350px; line-height:150%; border:1px solid rgba(0,0,0,.2);}
    </style>
    <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.css" />
    <script type="text/javascript" src="http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.js"></script>
    <script type="text/javascript" src="https://cdn.rawgit.com/pa7/heatmap.js/4e64f5ae/build/heatmap.js"></script>
    <script type="text/javascript" src="https://cdn.rawgit.com/pa7/heatmap.js/4e64f5ae/plugins/leaflet-heatmap/leaflet-heatmap.js"></script>
  </head>
  <body>
   <div id="map"></div>

    <script>
      window.onload = function() {

        var testData = {
)";

static const std::string html_footer =
R"(

        var baseLayer = L.tileLayer(
          'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
            maxZoom: 18
          }
        );

        var heatmapLayer = new HeatmapOverlay(cfg);

        var map = new L.Map('map', {
          center: new L.LatLng(41.9057514,12.442601),
          zoom: 6,
          layers: [baseLayer, heatmapLayer]
        });

        heatmapLayer.setData(testData);

        // make accessible for debugging
        layer = heatmapLayer;
      };
    </script>
  </body>
</html>
)";
