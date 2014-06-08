cmake_minimum_required(VERSION 2.8)
project(boost_python_ros)

find_package(catkin REQUIRED sensor_msgs nav_msgs std_msgs)

catkin_package()

catkin_python_setup()

find_package(Threads REQUIRED)
find_package(Boost COMPONENTS
  python
  thread
  system
  REQUIRED
  )
find_package(PythonLibs REQUIRED)



set(GEN_DIR_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/munged)
set(GEN_SHARED_LIBRARY_DIR ${GEN_DIR_ROOT})
set(GEN_PYTHON_ROOT ${GEN_DIR_ROOT})

file(WRITE ${GEN_DIR_ROOT}/__init__.py "\n")
file(WRITE ${GEN_SHARED_LIBRARY_DIR}/__init__.py "\n")
file(WRITE ${GEN_PYTHON_ROOT}/__init__.py "\n")


# We need a special library for the ros time types since these are ROS builtins that don't have .msg files
add_library(rostime_boost_python src/rostime_exports.cpp)
set_target_properties(rostime_boost_python
  PROPERTIES
  PREFIX ""
)
target_link_libraries(rostime_boost_python 
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
  )


# This macro generates the boost python bindings for the messages in a given ros package
macro(bpmodule NAME)
    include_directories(
      ${PYTHON_INCLUDE_PATH}
      ${Boost_INCLUDE_DIRS}
    )

    add_library(${NAME}_cpp SHARED ${ARGN})
    target_link_libraries(${NAME}_cpp ${${PROJECT_NAME}_LIBRARIES})
    
    
    set_target_properties(${NAME}_cpp
      PROPERTIES
      OUTPUT_NAME ${NAME}_cpp
      LIBRARY_OUTPUT_DIRECTORY ${GEN_SHARED_LIBRARY_DIR}
      PREFIX ""
    )
    
    target_link_libraries(${NAME}_cpp
      ${Boost_LIBRARIES}
      ${PYTHON_LIBRARIES}
      rostime_boost_python
    )
endmacro()


#attempts to set ENV variables so that ROS commands will work.
#This appears to work well on linux, but may be questionable on
#other platforms.
macro (_set_ros_env)
  set(ORIG_ROS_ROOT $ENV{ROS_ROOT})
  set(ORIG_ROS_PACKAGE_PATH $ENV{ROS_PACKAGE_PATH})
  set(ORIG_PATH $ENV{PATH})
  set(ORIG_PYTHONPATH $ENV{PYTHONPATH})
  set(ENV{ROS_ROOT} $ENV{ROS_ROOT})
  set(ENV{ROS_PACKAGE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}:$ENV{ROS_PACKAGE_PATH}")
  set(ENV{PATH} "${ROS_ROOT}/bin:$ENV{PATH}")
  set(ENV{PYTHONPATH} "${ROS_ROOT}/core/roslib/src:$ENV{PYTHONPATH}:${CMAKE_CURRENT_SOURCE_DIR}/src/")
endmacro()

#unset environment
macro (_unset_ros_env)
  set(ENV{ROS_ROOT} ${ORIG_ROS_ROOT})
  set(ENV{ROS_PACKAGE_PATH} ${ORIG_ROS_PACKAGE_PATH})
  set(ENV{PATH} "${ORIG_PATH}")
  set(ENV{PYTHONPATH} "${ORIG_PYTHONPATH}")
endmacro()

# Top level macro generates bindings as well as python conversion wrapper
macro(message_gen_wrap ROS_PACKAGE)
    set(GEN_DIR ${CMAKE_CURRENT_BINARY_DIR}/${ROS_PACKAGE}) #this is for generated cpp files.

    find_program(BOOST_PYTHON_GENERATE_PKG_BINDINGS
      generate_pkg_bindings.py
      PATHS ${CMAKE_CURRENT_SOURCE_DIR}/scripts
      NO_DEFAULT_PATH)

    _set_ros_env()
    execute_process(COMMAND ${BOOST_PYTHON_GENERATE_PKG_BINDINGS}
      --package=${ROS_PACKAGE}
      --cpp_target_dir=${GEN_DIR}
      --py_target_dir=${GEN_PYTHON_ROOT}
      --current_package=${PROJECT_NAME}
    )
    _unset_ros_env()

    file(GLOB ${ROS_PACKAGE}_srcs  ${GEN_DIR}/*.cpp)
    
    bpmodule(${ROS_PACKAGE}
        ${${ROS_PACKAGE}_srcs}
    )
endmacro()



message_gen_wrap(std_msgs)
message_gen_wrap(geometry_msgs)
message_gen_wrap(sensor_msgs)
message_gen_wrap(nav_msgs)
