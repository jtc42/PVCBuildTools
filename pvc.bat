@echo off
setlocal ENABLEDELAYEDEXPANSION

:: Path to vinyl script
SET VINYL_PATH=%~dp0\python_visual_c
SET BUILD_FILE="%VINYL_PATH%\vinyl.py"
SET TEMPL_FILE="%VINYL_PATH%\vinyl.txt"

IF "%1" == "generate" (
    ECHO "GENERATING TEMPLATE VINYL"
    CALL COPY %TEMPL_FILE% "%cd%\vinyl.txt"
) ELSE (
    :: Set dev env path to current cmd path
    SET "VSCMD_START_DIR="%cd%""

    :: Get build path
    IF NOT [%1]==[] (
        ECHO Using argument for build path
        SET BUILD_PATH=%1
    ) ELSE (
        ECHO Using current directory for build path
        SET BUILD_PATH="%cd%"
    )
    :: Delay parsing of BUILD_PATH until after IF statements have been evaluated, using !...!
    :: Call vcvars, and build argument 1 with cl
    CALL python %BUILD_FILE% !BUILD_PATH!
)