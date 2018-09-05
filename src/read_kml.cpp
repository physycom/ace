// parsekml.cc
// This program parses a KML Placemark from a memory buffer and prints
// the value of the <name> element on standard output.

#include <iostream>
#include <string>
#include "kml/dom.h"
#include "kml/engine.h"

int main() {
  // Parse KML from a memory buffer.
  std::string errors;
  kmldom::ElementPtr element = kmldom::Parse(
    "<kml>"
      "<Placemark>"
        "<name>hi</name>"
        "<Point>"
          "<coordinates>1,2,3</coordinates>"
        "</Point>"
      "</Placemark>"
    "</kml>",
    &errors);

  // Convert the type of the root element of the parse.
  const kmldom::KmlPtr kml = kmldom::AsKml(element);
  const kmldom::PlacemarkPtr placemark =
    kmldom::AsPlacemark(kml->get_feature());

  // Access the value of the <name> element.
  std::cout << "The Placemark name is: " << placemark->get_name()
    << std::endl;

  // We have just read the contents of a file into a string called file_data. We
  // believe it to be a KMZ and would like to:
  // - ensure it really is a KMZ file
  // - read the default KML file from the archive
  // - get a list of all files contained within the archive
  // - read a file called "images/pic.jpg" from the archive

  std::string file_data;
  std::string kml_s;
  // Ensure that the file is really a KMZ file.
  if (!kmlengine::KmzFile::IsKmz(file_data)) {
    // Handle error.
  }
  // Instantiate the KmzFile object.
  kmlengine::KmzFile* kmz_file = kmlengine::KmzFile::OpenFromString(file_data);
  if (!kmz_file) {
    // Handle error.
  }
  if (!kmz_file->ReadKml(&kml_s)) {
    // Handle error.
  }
  // `kml_s` is now a string filled with the raw XML for the default KML file.
  // We'll read the names of the archived files into a vector.
  std::vector<std::string> list;
  kmz_file->List(&list);
  // Now read "images/pic.jpg".
  std::string pic_data;
  if (!kmz_file->ReadFile("images/pic.jpg", &pic_data)) {
    // Handle error.
  }
  // Now delete the KmzFile instance when we're done with it.
  // There's a handy scoped_ptr in third_party you could use instead.
  delete kmz_file;
}
