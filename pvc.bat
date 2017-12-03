@echo off

:: Path to vinyl script
SET BUILD_FILE="%~dp0\python_visual_c\vinyl.py"

:: Get build path
IF NOT [%1]==[] (
    ECHO Using argument for build path
    SET BUILD_PATH="%~1"
) ELSE (
    ECHO Using current directory for build path
    SET BUILD_PATH="%cd%"
)

:: Call builder script
CALL python %BUILD_FILE% %BUILD_PATH%
