
find_path(GLIBMM_INCLUDE_DIR NAMES glibmm.h PATH_SUFFIXES glibmm-2.4)
find_library(GLIBMM_LIBRARY NAMES glibmm glibmm-2.4)
find_library(GLIB_LIBRARY NAMES glib glib-2.0)
find_package(LibXml2)

find_path(LibXmlpp_INCLUDE_DIR NAMES libxmlpp/libxmlpp.h libxml++/libxml++.h PATH_SUFFIXES libxml++-2.6)
find_library(LibXmlpp_LIBRARY NAMES xmlpp xmlpp-2.6 xml++ xml++-2.6)

set(LibXmlpp_INCLUDE_DIRS ${LibXmlpp_INCLUDE_DIR} ${GLIBMM_INCLUDE_DIR} ${LIBXML2_INCLUDE_DIR})
set(LibXmlpp_LIBRARIES ${LibXmlpp_LIBRARY} ${GLIBMM_LIBRARY} ${LIBXML2_LIBRARIES})

message(STATUS "${LibXmlpp_INCLUDE_DIRS}")
message(STATUS "${LibXmlpp_LIBRARIES}")

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(LibXmlpp DEFAULT_MSG LibXmlpp_LIBRARY LibXmlpp_INCLUDE_DIR)

MARK_AS_ADVANCED(LibXmlpp_INCLUDE_DIR LibXmlpp_LIBRARY)
