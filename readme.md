# PVC Build Tools

## What is this?
Compiling using Visual Studio Build Tools on Windows, using the command line, is a minor pain. One shared by a few people out there I'm sure. This Python script aims to alleviate this pain. It's a bit like CMake, but worse, but simpler. 

Using a tiny json file in your source directory, `press.py` generates a build script that drops you into the correct VS environment, and compiles. It has some neat stuff like automatically finding Python and Numpy include/library directories, and will hopefully soon automatically find CUDA directories too.

So far it supports the `cl` and `nvcc` compilers, with possibly broken support for `gcc` and `g++`.

## How-to
* Edit `PVCBuildTools\pvc\config.json` file to set your `vcvarsall` and CUDA directories.
* Add the 'PVCBuildTools' folder to your PATH environment variable.
* Add .PY to your PATHTEXT environment variable
* In your source directory, create a .json in the format below.
  * Alternatively, run `makevinyl` in your source directory to easy-generate a *basic* vinyl.json.
* Run `press <path to vinyl json>` (or `press.py <path to vinyl json>`).

## Example vinyl.json
```
{
  "compiler": "cl",
  "vcvars_ver": 14.11,
  
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
|**vcvars_ver**|(number) (optional)|Specify a version of MSVC to build with. Eg. 14.11 for building CUDA|
|**arch**|(string) (optional)|Architecture to build for. Eg. "x64", "x86". If missing, defaults to hosts architecture. |
|**flags**|(list of strings) (optional)|General build flags. Currently supports "shared", to build a shared library, and "debug" to build a debug output.|
|**options**|(list of strings) (optional)|List of additional flags to pass directly to the compiler. Allows passing of arbitrary arguments for stuff not supported in PVC yet.|
|**source**|(list of strings) (required)|Relative paths to source file(s) to build.|
|**include**|(list of strings) (required)|Paths to additional include directories. *Supports AUTOPARAMS (see below)*|
|**libs**|(list of strings) (required)|Paths to additional library directories. *Supports AUTOPARAMS (see below)*|
|**out**|(string) (required)|Full name/path of output file.|
  
  
## Autoparams
Autoparams allow the automatic inclusion of INCLUDE and LIB directories, based on keywords. For example, Python and CUDA libraries can be automatically found and added to the build command.

To add an autoparam, wrap a supported keyword in $$, as below:

| Keyword  | Compatible properties | Notes |
| ------------- | ------------- | ------------- |
|**$C$**|compiler|Runs cl.exe on Windows, and gcc everywhere else|
|**$C++$**|compiler|Runs cl.exe on Windows, and g++ everywhere else|
|**$PYTHON$**|include, libs|Finds directory of Python interpreter, and adds includes and libs required to build Python extensions|
|**$NUMPY$**|include|Finds directory of numpy package, and adds includes required to build Python extensions using Numpy C API|
|**$CUDA$**|include, libs|Finds directory of CUDA installation from 'config.json', and adds includes required to build CUDA code with nvcc compiler|
