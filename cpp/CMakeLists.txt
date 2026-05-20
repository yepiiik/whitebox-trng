cmake_minimum_required(VERSION 3.10)
project(TRNG)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add executable
add_executable(trng main.cpp)

# Find OpenSSL
find_package(OpenSSL REQUIRED)
target_link_libraries(trng PRIVATE OpenSSL::Crypto)

# Optional: Add compiler flags for optimization
if(MSVC)
    target_compile_options(trng PRIVATE /W4)
else()
    target_compile_options(trng PRIVATE -Wall -Wextra -Wpedantic)
endif()
