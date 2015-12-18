cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

#include(FindBoost)
find_package(Boost REQUIRED COMPONENTS system)
#find_package(Boost ${MIN_BOOST_VERSION} REQUIRED system filesystem regex)
include_directories(${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})

find_package(OpenCV REQUIRED COMPONENTS core imgproc)
include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIBRARY_DIRS})

find_package(Protobuf REQUIRED)

include (FindPkgConfig)
if (PKG_CONFIG_FOUND)
  pkg_check_modules(GAZEBO gazebo)
else()
  message(FATAL_ERROR "pkg-config is required; please install it")
endif()
include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

# compile plugin
add_library(pt_ach_ctl SHARED pt_ach_ctl.cc)
target_link_libraries(pt_ach_ctl ${GAZEBO_LIBRARIES} ${Boost_LIBRARIES} pthread ach)

add_executable(video_listener video_listener.cc)
target_link_libraries(video_listener ${GAZEBO_LIBRARIES} ${Boost_LIBRARIES} ${PROTOBUF_LIBRARIES} opencv_core opencv_imgproc pthread ach)

#add_library(animate_pose SHARED animate_pose.cc)
#target_link_libraries(animate_pose ${GAZEBO_LIBRARIES} ${Boost_LIBRARIES} pthread ach)

