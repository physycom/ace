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


#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <map>
#include <string>
#include <iterator>
#include <cfloat>

#include <physycom/string.hpp>
#include "error_codes.h"
#include "header_html.h"

#define SEPARATORS       ", \t"
#define COMMENTS         "#"

#define MAJOR_VERSION    0
#define MINOR_VERSION    1

void usage(char* );
std::vector<std::vector<std::string>> Parse_file(std::string, std::string, std::string);
std::vector<std::vector<double>> Convert_to_double_vector(std::vector<std::vector<std::string>>);
void find_min_max_count(std::vector<std::vector<double>> &, double &, double &);
void dump_html(std::vector<std::vector<std::string>> &, std::string, size_t);


int main(int argc, char*argv[])
{
  std::cout << argv[0] << " v. " << MAJOR_VERSION << '.' << MINOR_VERSION << std::endl;
  if (argc != 3) {
    usage(argv[0]);
    exit(INSUFFICIENT_COMMAND_LINE_PARAMETERS);
  }

  std::string filename_in = std::string(argv[1]);
  std::string filename_out = std::string(argv[2]);

  std::vector<std::vector<std::string>> parsed_file = Parse_file(filename_in, SEPARATORS, COMMENTS);
  std::vector<std::vector<double>> doubled_file = Convert_to_double_vector(parsed_file);
  double min_count, max_count;
  find_min_max_count(doubled_file, min_count, max_count);
  //dump_html(parsed_file, filename_out, size_t(max_count));
  dump_html(parsed_file, filename_out, 100);

  return 0;
}



bool Belongs_to(char c, std::string s) {
  for (size_t i = 0; i < s.size(); i++) { if (c == s.at(i)) return true; }
  return false;
}



std::vector<std::vector<std::string>> Parse_file(std::string file_name, std::string separators, std::string comment) {
  std::ifstream file_to_parse(file_name, std::ios::in);
  if (!file_to_parse) {
    std::cout << "Cannot open " << file_name << ". Quitting..." << std::endl;
    exit(12);
  }
  std::string line;
  std::vector<std::string> tokens;
  std::vector<std::vector<std::string>> parsed;
  while (getline(file_to_parse, line)) {
    if (Belongs_to(line[0], comment) || !line.size()) continue;
    physycom::split(tokens, line, separators);
    for (size_t i = 0; i < tokens.size(); i++) {
      if (Belongs_to(tokens[i][0], comment)) { tokens.erase(tokens.begin() + i, tokens.end()); }
    }
    if (tokens.size()) {
      parsed.push_back(tokens);
    }
    line.clear(); tokens.clear();
  }
  file_to_parse.close();
  return parsed;
}



std::vector< std::vector<double> > Convert_to_double_vector(std::vector< std::vector<std::string> > parsed_file) {
  std::vector<double> doubled_line;
  std::vector< std::vector<double> > doubled_file;

  for (auto &i : parsed_file) {
    doubled_line.clear();
    doubled_line.resize(i.size());
    for (size_t j = 0; j < i.size(); j++) doubled_line[j] = atof(i[j].c_str());
    doubled_file.push_back(doubled_line);
  }
  return doubled_file;
}



void find_min_max_count(std::vector<std::vector<double>> &doubled_file, double &min_val, double &max_val) {
  max_val = -DBL_MAX;
  min_val =  DBL_MAX;
  for (auto &i : doubled_file) {
    for (size_t j = 2; j < i.size() ; j++) {
      if (i[j] > max_val) max_val = i[j];
      if (i[j] < min_val) min_val = i[j];
    }
  }
}



void usage(char* progname) {
  std::string pn(progname);
  std::cerr << "Usage: " << pn.substr(pn.find_last_of("/\\")+1) << " input.csv output.html" << std::endl;
}



void dump_html(std::vector<std::vector<std::string>> &parsed_file, std::string file_name, size_t max_val) {
  std::stringstream output;
  output << html_header;
  size_t max_column_number = parsed_file[0].size();
  if (max_column_number > 10) max_column_number = 10;

  for (size_t c = 2 ; c < max_column_number ; ++c) {
    output << "        var data_" << c << " = {" << std::endl;
    output << "          max: " << max_val << ",\n          data: [";
    for (size_t i = 0 ; i < parsed_file.size() ; ++i) {
      std::string lat = parsed_file[i][0];
      std::string lng = parsed_file[i][1];
      std::string count = parsed_file[i][c];
      output << "{lat: " << lat << ", lng:" << lng << ", count: " << count << "}";
      if (i != parsed_file.size()-1) output << ",";
    }
    output << "]" << std::endl;
    output << "        };" << std::endl;
    output << "        animationData.push(data_" << c << ");" << std::endl;
  }

  // radius should be small ONLY if scaleRadius is true (or small radius is intended)
  double radius = 0.3;
  double maxOpacity = 0.8;
  // scales the radius based on map zoom
  bool scaleRadius = true;
  // if set to false the heatmap uses the global maximum for colorization
  // if activated: uses the data maximum within the current map boundaries
  //   (there will always be a red spot with useLocalExtremas true)
  bool useLocalExtrema = true;
  // which field name in your data represents the latitude - default "lat"
  std::string latField = "lat";
  // which field name in your data represents the longitude - default "lng"
  std::string lngField = "lng";
  // which field name in your data represents the data value - default "value"
  std::string valueField = "count";
  output << "        var cfg = {" << std::endl;
  output << "          \"radius\": " << radius << "," << std::endl;
  output << "          \"maxOpacity\": " << maxOpacity << "," << std::endl;
  output << std::boolalpha;
  output << "          \"scaleRadius\": " << scaleRadius << "," << std::endl;
  output << "          \"useLocalExtrema\": " << useLocalExtrema << "," << std::endl;
  output << std::noboolalpha;
  output << "          \"latField\": '" << latField << "'," << std::endl;
  output << "          \"lngField\": '" << lngField << "'," << std::endl;
  output << "          \"valueField\": '" << valueField << "'"<< std::endl;
  output << "        };" << std::endl;

  output << html_footer;

  std::ofstream dump_html(file_name);
  dump_html << output.rdbuf();
  dump_html.close();
}
