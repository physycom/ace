#include <cstdio>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <streambuf>
#include <string>
#include <kml/dom.h>
#include <kml/engine.h>
#include <kml/base/file.h>
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/HTMLparser.h>
#include "error_codes.h"


int main(int argc, char*argv[]) {

  //kmlbase::File::ReadFileToString(argv[1], &file_data)
  std::ifstream t(argv[1], std::ios_base::in|std::ios_base::binary);
  if (!t.is_open() || !t.good()) {
    std::cerr << "Unable to find file: " << argv[1] << std::endl;
    exit(FILE_NOT_FOUND);
  }

  std::string kmz_data((std::istreambuf_iterator<char>(t)),
      std::istreambuf_iterator<char>());

  // Ensure that the file is really a KMZ file.
  if (!kmlengine::KmzFile::IsKmz(kmz_data)) {
    std::cerr << "File is not a valid KMZ object" << std::endl;
    exit(INVALID_KMZ);
  }

  // Instantiate the KmzFile object.
  kmlengine::KmzFile* kmz_file = kmlengine::KmzFile::OpenFromString(kmz_data);
  if (!kmz_file) {
    std::cerr << "String does not contain valid KMZ data" << std::endl;
    exit(INVALID_KMZ);
  }

  std::string kml_s;
  if (!kmz_file->ReadKml(&kml_s)) {
    std::cerr << "Invalid KML syntax" << std::endl;
    exit(INVALID_KML);
  }

  // `kml_s` is now a string filled with the raw XML for the default KML file.
  std::string errors;
  kmldom::ElementPtr element = kmldom::Parse(kml_s, &errors);

  std::vector<kmldom::ElementPtr> placemarks;
  kmlengine::GetElementsById(element, kmldom::Type_Placemark, &placemarks);

  for (auto pm : placemarks) {
    kmldom::PlacemarkPtr ppm = AsPlacemark(pm);
    std::string name = ppm->get_name();
    std::string id = ppm->get_id();
    id = id.substr(3, id.size()-3);
    std::string descr = ppm->get_description();

    unsigned char *u_descr = new unsigned char[descr.size()];
    std::copy(descr.begin(), descr.begin() + descr.size(), u_descr);

    int cod_istat = 0;
    int cod_ace = 0;
    std::string base_url = "unknown.website";
    std::string encoding = "UTF-8";

    htmlDocPtr doc = NULL;
    doc = htmlReadDoc(u_descr, base_url.c_str(), encoding.c_str(), HTML_PARSE_NOBLANKS | HTML_PARSE_NOERROR | HTML_PARSE_NOWARNING | HTML_PARSE_NONET);
    //doc = htmlReadDoc(u_descr, base_url.c_str(), encoding.c_str(), HTML_PARSE_RECOVER | HTML_PARSE_PEDANTIC);

    if (doc == NULL) {
      std::cerr << "Document not parsed successfully" << std::endl;
      exit(INVALID_NESTED_HTML);
    }

    xmlNode *root_node = xmlDocGetRootElement(doc);

    if (root_node == NULL) {
      std::cerr << "Document empty" << std::endl;
      exit(EMPTY_NESTED_HTML);
    }

    bool cod_istat_found = false;
    bool cod_ace_found = false;
    xmlChar *key;
    int istat_value = 0;
    int ace_value = 0;
    for (xmlNode *body_node = root_node->children; body_node; body_node = body_node->next) {
      if (!xmlStrcmp(body_node->name, (const xmlChar *)"body")) {
        for (xmlNode *table_node = body_node->children; table_node; table_node = table_node->next) {
          if (!xmlStrcmp(table_node->name, (const xmlChar *)"table")) {
            for (xmlNode *tr_node = table_node->children; tr_node; tr_node = tr_node->next) {
              if (!xmlStrcmp(tr_node->name, (const xmlChar *)"tr")) {
                for (xmlNode *td_node = tr_node->children; td_node; td_node = td_node->next) {
                  if (!xmlStrcmp(td_node->name, (const xmlChar *)"td") && xmlChildElementCount(td_node) > 0) {
                    for (xmlNode *inner_table_node = td_node->children; inner_table_node; inner_table_node = inner_table_node->next) {
                      if (!xmlStrcmp(inner_table_node->name, (const xmlChar *)"table")) {
                        for (xmlNode *inner_tr_node = inner_table_node->children; inner_tr_node; inner_tr_node = inner_tr_node->next) {
                          if (!xmlStrcmp(inner_tr_node->name, (const xmlChar *)"tr")) {
                            for (xmlNode *inner_td_node = inner_tr_node->children; inner_td_node; inner_td_node = inner_td_node->next) {
                              if (!xmlStrcmp(inner_td_node->name, (const xmlChar *)"td")) {
                                key = xmlNodeListGetString(doc, inner_td_node->xmlChildrenNode, 1);
                                if (xmlStrcmp(key, (const xmlChar *)"COD_ISTAT") && xmlStrcmp(key, (const xmlChar *)"ACE")) break;
                                if (!xmlStrcmp(key, (const xmlChar *)"COD_ISTAT")){
                                  cod_istat_found = true;
                                  inner_td_node = inner_td_node->next;
                                  if (inner_td_node) {
                                    inner_td_node = inner_td_node->next;
                                    if (inner_td_node) {
                                      key = xmlNodeListGetString(doc, inner_td_node->xmlChildrenNode, 1);
                                      try {
                                        std::string content((char*)key);
                                        istat_value = std::stoi(content);
                                      }
                                      catch(...) {}
                                    }
                                  }
                                }
                                if (!xmlStrcmp(key, (const xmlChar *)"ACE")){
                                  cod_ace_found = true;
                                  inner_td_node = inner_td_node->next;
                                  if (inner_td_node) {
                                    inner_td_node = inner_td_node->next;
                                    if (inner_td_node) {
                                      key = xmlNodeListGetString(doc, inner_td_node->xmlChildrenNode, 1);
                                      try {
                                        std::string content((char*)key);
                                        ace_value = std::stoi(content);
                                      }
                                      catch(...) {}
                                    }
                                  }
                                }
                              }
                            }
                            if (cod_istat_found) cod_istat = istat_value, cod_istat_found = false;
                            if (cod_ace_found) cod_ace = ace_value, cod_ace_found = false;
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    xmlFree(key);
    xmlFreeDoc(doc);
    xmlCleanupParser();

    double lat, lon;
    if (!kmlengine::GetFeatureLatLon(ppm, &lat, &lon)) {
      std::cerr << "Unable to find lat/lon for this placemark, KML not valid" << std::endl;
      exit(MISSING_LAT_LON);
    }

    std::stringstream istat_full_ace;
    istat_full_ace << std::setfill('0') << std::setw(9) << cod_istat << 'C' << std::setw(3) << cod_ace << std::flush;
    std::cout << istat_full_ace.str() << ',' << lat << ',' << lon << std::endl;
  }

  delete kmz_file;
}
