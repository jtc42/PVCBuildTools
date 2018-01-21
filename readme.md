# PVC Build Tools

## How-to
* Add 'PVCBuildTools' folder to PATH environment variable
* In your source directory, create vinyl.json in format below
* Run 'pvc' in directory containing vinyl.json, or run 'pvc \<path to source folder>' from anywhere

## Example vinyl.json
```
{
  "compiler": "cl",
  "msvcver": 14.11,
  
  "arch": [
    "x64",
    "x86"
  ],

  "flags": [
    "debug"
  ],

  "options": [],

  "source": [
    "main.cpp"
  ],

  "include": ["$PYTHON$"],
  "libs": ["$PYTHON$"],

  "out": "out.exe"
}
```

## Vinyl properties

| Property  | Type | Notes |
| ------------- | ------------- | ------------- |
|**compiler**|(string) (required)|Compiler to build with. Currently supports "cl", and "nvcc".|
|**msvcver**|(number) (optional)|Specify a version of MSVC to build with. Eg. 14.11 for building CUDA|
|**arch**|(string, or list of strings) (optional)|Architecture(s) to build for. Eg. "x64", "x86", or ["x64","x86"]. If missing, defaults to hosts architecture. |
|**flags**|(list of strings) (optional)|General build flags. Currently supports "shared", to build a shared library, and "debug" to build a debug output.|
|**options**|(list of strings) (optional)|List of additional flags to pass directly to the compiler. Allows passing of arbitrary arguments for stuff not supported in PVC yet.|
|**source**|(list of strings) (required)|Relative path to source file(s) to build.|
|**include**|(list of strings) (required)|Paths to additional include directories. *Supports AUTOPARAMS (see below)*|
|**libs**|(list of strings) (required)|Paths to additional library directories. *Supports AUTOPARAMS (see below)*|
|**out**|(string) (required)|Full name of output file. File will be moved to '<source directory>/build/<architecture>'.|
  
  
## Autoparams
Autoparams allow the automatic inclusion of INCLUDE and LIB directories, based on keywords. For example, Python and CUDA libraries can be automatically found and added to the build command.

To add an autoparam, wrap a supported keyword in $$, as below:

| Keyword  | Compatible properties | Notes |
| ------------- | ------------- | ------------- |
|**$PYTHON$**|include, libs|Finds directory of Python interpreter, and adds includes and libs required to build Python extensions|
|**$NUMPY$**|include|Finds directory of numpy package, and adds includes required to build Python extensions using Numpy C API|
|**$CUDA$**|include, libs|Finds directory of CUDA installation from 'config.json', and adds includes required to build CUDA code with nvcc compiler|
