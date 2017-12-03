@echo on

:: Sets the default vcvars file, and build target
SET VCVARS_FILE="C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"

:: Find host architecture
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=x86 || set OS=x64

:: Set dev env path to current cmd path
SET "VSCMD_START_DIR='%cd%'"

:: Call vcvars, and build argument 1 with cl
CALL %VCVARS_FILE% %OS%
CALL nmake