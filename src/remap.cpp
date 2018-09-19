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
#include <map>
#include <string>
#include <iterator>

#include <physycom/string.hpp>

#include "error_codes.h"

#define SEPARATORS       " \t"
#define COMMENTS         "#"
#define MAJOR_VERSION    0
#define MINOR_VERSION    1

bool Belongs_to(char, std::string);
std::vector<std::vector<std::string>> Parse_file(std::string, std::string, std::string);


int main(int argc, char*argv[])
{
  std::cout << argv[0] << " v. " << MAJOR_VERSION << '.' << MINOR_VERSION << std::endl;
  std::string filename;
  filename = std::string(argv[1]);

  std::vector< std::vector<std::string> > parsed_file = Parse_file(filename, SEPARATORS, COMMENTS);
  std::map<std::string, std::string> mapOfAces;

  std::string aceID = "aceID";
  std::string latlon = "lat,lon";

  // Insert and check if insertion is successful
  if(mapOfAces.insert(std::make_pair(aceID, latlon)).second == false) {
    std::cerr << "Element with key " << aceID << " not inserted because already existed" << std::endl;
  }

  std::map<std::string, std::string>::iterator it = mapOfAces.begin();
  while(it != mapOfAces.end()) {
    std::cout<<it->first<<" :: "<<it->second<<std::endl;
    it++;
  }

  // Searching element in std::map by key.
  if(mapOfAces.find(aceID) != mapOfAces.end()) {
    std::cout << "Element with key " << aceID << " found" << std::endl;
  }

  return 0;
}



bool Belongs_to(char c, std::string s) {
  for (size_t i = 0; i < s.size(); i++) { if (c == s.at(i)) return true; }
  return false;
}



std::vector< std::vector<std::string> > Parse_file(std::string file_name, std::string separators, std::string comment) {
  std::ifstream file_to_parse(file_name, std::ios::in);
  if (!file_to_parse) {
    std::cout << "Cannot open " << file_name << ". Quitting..." << std::endl;
    exit(12);
  }
  std::string line;
  std::vector<std::string> tokens;
  std::vector< std::vector<std::string> > parsed;
  while (getline(file_to_parse, line)) {
    if (Belongs_to(line[0], comment) || !line.size()) continue;
    physycom::split(tokens, line, std::string(separators));
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


