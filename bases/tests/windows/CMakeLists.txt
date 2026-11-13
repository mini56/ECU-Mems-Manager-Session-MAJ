cmake_minimum_required(VERSION 3.16)
project(MEMS_DOCUMENTARY_REAL_WINDOWS_INSTALL LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT SESSION_SOURCE_ROOT)
    message(FATAL_ERROR "SESSION_SOURCE_ROOT is required")
endif()
find_package(Qt5 REQUIRED COMPONENTS Core Sql Network)
add_executable(real_documentary_install
    real_documentary_install.cpp
    "${SESSION_SOURCE_ROOT}/database/MemsDocumentaryLocalInstaller.cpp"
    "${SESSION_SOURCE_ROOT}/database/MemsDocumentaryEncryptedPack.cpp"
    "${SESSION_SOURCE_ROOT}/database/MemsDocumentaryPackCatalog.cpp"
)
target_include_directories(real_documentary_install PRIVATE
    "${SESSION_SOURCE_ROOT}/database")
target_link_libraries(real_documentary_install PRIVATE
    Qt5::Core Qt5::Sql Qt5::Network bcrypt)
if(MSVC)
    target_compile_options(real_documentary_install PRIVATE /utf-8)
endif()
