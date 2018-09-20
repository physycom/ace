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
#include <fstream>
#include <sstream>
#include <map>
#include <string>
#include <iterator>

#include <physycom/string.hpp>
#include <jsoncons/json.hpp>

#include "error_codes.h"

#define SEPARATORS       ","
#define COMMENTS         "#"

#define MAJOR_VERSION    0
#define MINOR_VERSION    2

void usage(char* );
bool Belongs_to(char, std::string);
std::vector<std::vector<std::string>> Parse_file(std::string, std::string, std::string);
std::vector<std::vector<std::string>> Rebuild_lat_lon(std::vector<std::vector<std::string>>&);
jsoncons::json prepare_json_from_map(std::map<std::string, std::string> &);
jsoncons::json prepare_json_from_vector(std::vector<std::vector<std::string>> &);
void dump_map(std::map<std::string, std::string> &);
void dump_vector(std::vector<std::vector<std::string>> &);


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
  std::vector<std::vector<std::string>> vectorOfAces = Rebuild_lat_lon(parsed_file);

  std::map<std::string, std::string> mapOfAces;
  size_t duplicated_records = 0;

  for (auto line : vectorOfAces) {
    std::string aceID = line[0];
    std::string latlon = line[1];

    // Insert and check if insertion is successful
    if(mapOfAces.insert(std::make_pair(aceID, latlon)).second == false) {
      duplicated_records++;
      //std::cerr << "Element with key " << aceID << " not inserted because already existed" << std::endl;
    }
  }

  std::cout << duplicated_records << " duplicated records were found in the csv." << std::endl;
  //jsoncons::json records = prepare_json_from_vector(vectorOfAces);
  jsoncons::json records = prepare_json_from_map(mapOfAces);

  //dump_map(mapOfAces);
  //dump_vector(vectorOfAces);

  std::ofstream json_file(filename_out);
  json_file << jsoncons::pretty_print(records) << std::endl;
  json_file.close();
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



std::vector<std::vector<std::string>> Rebuild_lat_lon(std::vector<std::vector<std::string>>& parsed_file) {
  std::vector<std::vector<std::string>> mapped_tokens;
  for (auto line : parsed_file) {
    if (line.size() != 3) {
      std::cerr << "Unexpected line length: " << line.size() << std::endl;
      exit(UNEXPECTED_LINE_LENGTH);
    }
    std::string aceID = line[0];
    std::string latlon = line[1] + ',' + line[2];
    std::vector<std::string> mapped_token;
    mapped_token.push_back(aceID);
    mapped_token.push_back(latlon);
    mapped_tokens.push_back(mapped_token);
  }
  return mapped_tokens;
}



jsoncons::json prepare_json_from_map(std::map<std::string, std::string>& mapOfAces) {
  jsoncons::json records = jsoncons::json::array();
  std::map<std::string, std::string>::iterator it = mapOfAces.begin();
  while(it != mapOfAces.end()) {
    //std::cout<<it->first<<" :: "<<it->second<<std::endl;
    std::vector<std::string> tokens;
    std::string separators = SEPARATORS;
    physycom::split(tokens, it->second, separators);
    double lat, lon;
    try {
      lat = std::stod(tokens[0]);
      lon = std::stod(tokens[1]);
    }
    catch(std::exception &e) {
      std::cerr << "Unable to extract lat/lon from string in map: " << e.what() << std::endl;
      exit(FAILED_STOD);
    }
    jsoncons::json record;
    record["lon"] = lon;
    record["lat"] = lat;
    record["ace"] = it->first;
    records.add(record);
    ++it;
  }

  // Searching element in std::map by key.
  //if(mapOfAces.find(aceID) != mapOfAces.end()) {
  //  std::cout << "Element with key " << aceID << " found" << std::endl;
  //}
  return records;
}



jsoncons::json prepare_json_from_vector(std::vector<std::vector<std::string>> &vectorOfAces) {
  jsoncons::json records = jsoncons::json::array();
  std::vector<std::vector<std::string>>::iterator it = vectorOfAces.begin();
  while(it != vectorOfAces.end()) {
    //std::cout<<it->first<<" :: "<<it->second<<std::endl;
    std::vector<std::string> tokens;
    std::string separators = SEPARATORS;
    physycom::split(tokens, (*it)[1], separators);
    double lat, lon;
    try {
      lat = std::stod(tokens[0]);
      lon = std::stod(tokens[1]);
    }
    catch(std::exception &e) {
      std::cerr << "Unable to extract lat/lon from string in map: " << e.what() << std::endl;
      exit(FAILED_STOD);
    }
    jsoncons::json record;
    record["lon"] = lon;
    record["lat"] = lat;
    record["ace"] = (*it)[0];
    records.add(record);
    ++it;
  }

  // Searching element in std::map by key.
  //if(mapOfAces.find(aceID) != mapOfAces.end()) {
  //  std::cout << "Element with key " << aceID << " found" << std::endl;
  //}
  return records;
}



void usage(char* progname) {
  std::string pn(progname);
  std::cerr << "Usage: " << pn.substr(pn.find_last_of("/\\")+1) << " input.csv output.json" << std::endl;
}



void dump_map(std::map<std::string, std::string>& mapOfAces) {
  std::stringstream output;
  std::map<std::string, std::string>::iterator it = mapOfAces.begin();
  while(it != mapOfAces.end()) {
    //std::cout<<it->first<<" :: "<<it->second<<std::endl;
    std::vector<std::string> tokens;
    std::string separators = SEPARATORS;
    physycom::split(tokens, it->second, separators);
    double lat, lon;
    try {
      lat = std::stod(tokens[0]);
      lon = std::stod(tokens[1]);
    }
    catch(std::exception &e) {
      std::cerr << "Unable to extract lat/lon from string in map: " << e.what() << std::endl;
      exit(FAILED_STOD);
    }
    output << it->first << ' ' << lat << ' ' << lon << std::endl;
    ++it;
  }

  std::ofstream dump_map("map.txt");
  dump_map << output.rdbuf();
  dump_map.close();
}



void dump_vector(std::vector<std::vector<std::string>> &vectorOfAces){
  std::stringstream output;
  std::vector<std::vector<std::string>>::iterator it = vectorOfAces.begin();
  while(it != vectorOfAces.end()) {
    std::vector<std::string> tokens;
    std::string separators = SEPARATORS;
    physycom::split(tokens, (*it)[1], separators);
    double lat, lon;
    try {
      lat = std::stod(tokens[0]);
      lon = std::stod(tokens[1]);
    }
    catch(std::exception &e) {
      std::cerr << "Unable to extract lat/lon from string in map: " << e.what() << std::endl;
      exit(FAILED_STOD);
    }
    output << (*it)[0] << ' ' << lat << ' ' << lon << std::endl;
    ++it;
  }

  std::ofstream dump_vector("vector.txt");
  dump_vector << output.rdbuf();
  dump_vector.close();
}
