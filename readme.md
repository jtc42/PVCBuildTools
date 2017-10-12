# PVC Build Tools

## vinyl.txt format

COMPILER: CL/NVCC
ARCHITECTURE: x64/x86
SOURCE: <source_1>,<source_2>, ...
OUTPUT: <output_name>
PLATE: PYTHON, NUMPY
FORMAT: SHAREDLIB/EXECUTABLE, SINGLETHREAD/MULTITHREAD, DEBUG/RELEASE
INCLUDE: <include_path_1>, <include_path_2>, ...
LIBS: <lib_path_1>, <lib_path_2>, ...
OPTIONS: <Custom build flags, comma separated>