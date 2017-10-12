# PVC Build Tools

## How-to
* Add 'PVCBuildTools' folder to PATH environment variable
* Run 'pvc generate' in the source directory to create initial vinyl.txt
* Modify vinyl.txt by format below
* Run 'pvc' in directory containing vinyl.txt, or run 'pvc <path to source folder>' from anywhere

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
