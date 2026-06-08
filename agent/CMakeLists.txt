cmake_minimum_required(VERSION 3.10)
project(TelemetryAgent)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_executable(agent src/main.cpp)