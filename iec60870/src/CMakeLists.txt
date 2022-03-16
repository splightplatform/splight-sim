include_directories(
   .
)

set(example_SRCS
   iec60870_custom_server.c
)

IF(WIN32)
set_source_files_properties(${example_SRCS}
                                       PROPERTIES LANGUAGE CXX)
ENDIF(WIN32)

add_executable(iec60870-104-custom-server
  ${example_SRCS}
)

target_link_libraries(iec60870-104-custom-server
    lib60870
)
