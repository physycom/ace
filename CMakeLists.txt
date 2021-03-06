cmake_minimum_required (VERSION 3.1)
project (ace)

if (EXISTS "$ENV{WORKSPACE}/sysconfig/cmake/physycom_config.cmake")
   message(STATUS "Enabling physycom settings")
   include("$ENV{WORKSPACE}/sysconfig/cmake/physycom_config.cmake")
else()
   message(STATUS "Unable to find physycom settings file")
endif()

if(APPLE)
  set(KML_ROOT_DIR /usr/local/Cellar/libkml/1.2.0/)
endif()

find_package(KML REQUIRED)
find_package(LibXml2 REQUIRED)
if(MSVC)
  find_package(UriParser REQUIRED)
  find_package(MiniZip REQUIRED)
  find_package(ZLIB REQUIRED)
  find_package(BZip2 REQUIRED)
  list(APPEND ADDITIONAL_LIBRARIES ${URIPARSER_LIBRARY} ${ZLIB_LIBRARY} ${MINIZIP_LIBRARY} ${BZIP2_LIBRARY})
endif()
add_definitions("${LIBXML2_DEFINITIONS}")

set(PHYSYCOM_UTILS "${CMAKE_SOURCE_DIR}/src/utils")
set(JSONCONS "${CMAKE_SOURCE_DIR}/src/jsoncons/include")
include_directories(${KML_INCLUDE_DIRS} ${LIBXML2_INCLUDE_DIR} ${PHYSYCOM_UTILS} ${JSONCONS})

add_executable(remap ${CMAKE_SOURCE_DIR}/src/remap.cpp)
add_executable(animate ${CMAKE_SOURCE_DIR}/src/animate.cpp)

add_executable(ace ${CMAKE_SOURCE_DIR}/src/read_kml.cpp)
target_link_libraries(ace ${KML_LIBRARIES} ${LIBXML2_LIBRARIES} ${ADDITIONAL_LIBRARIES})
