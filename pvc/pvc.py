# -*- coding: utf-8 -*-
import json
from sysconfig import get_paths
import os
import platform
import subprocess
import sys
import logging
from jinja2 import Template
from copy import copy

from . import utilities


# FUNCTIONS
def find_executable(executable, path=None):
    """
    Borrowed liberally from techtonik/find_executable.py.
    Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        # executable files on OS/2 can have an arbitrary extension, but
        # .exe is automatically appended if no dot is present in the name
        if not ext:
            executable = executable + ".exe"
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None


def list2string(lst, separator=' '):
    """
    Convert a list of strings into a single, space-separated string
    """
    return separator.join(lst)


def subprocess_cmd(command, print_output = True):
    """
    Takes a command as a string, and runs it in a shell process
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].decode()
    
    if print_output:
        print(proc_stdout)
    return proc_stdout


def autoparams(parameter_dictionary):
    """
    Takes a parameter dictionary, and converts autoparam references to their full paths
    """
    global AUTOPARAMS

    for section, assignments in AUTOPARAMS.items():  # For each section in AUTOPARAMS
        if section in parameter_dictionary:  # If that section exists in the params dictionary

            # If that section is a list of items
            if type(parameter_dictionary[section]) == list:
                # If parameter dictionary section item is assigned in AUTO_PARAMS, use the assignment
                # Else just use the original string
                parameter_dictionary[section] = [assignments[l] if l in assignments else l for l in
                                                parameter_dictionary[section]]
            # If the section is a single value
            else:
                # If the section value is in the dictionary of AUTO_PARAM assignments
                if parameter_dictionary[section] in assignments:
                    # Replace section value with corresponding AUTO_PARAM assignment
                    parameter_dictionary[section] = assignments[parameter_dictionary[section]]

    print(parameter_dictionary)
    return parameter_dictionary

    
def win_env(params, path):
    """
    Constructs a command to set up VC environment in Windows, using vcvarsall
    """
    # Initially empty arguments to pass to vcvarsall
    vc_args = ''
    
    # Add arguments to vcvarsall based on params
    if params['vcvars_ver']:  # If MSVC version is specific
        # Use old version of MSVC
        vc_args = vc_args + '-vcvars_ver={} '.format(params['vcvars_ver'])
        
    # Create command for start directory
    cdd = 'SET "VSCMD_START_DIR=""{}"""'.format(path)
    # Create command for environment
    env = 'CALL "' + os.path.join(VCVARS_PATH, "vcvarsall.bat") + '" ' + params['arch'] + ' ' + vc_args
    
    # Join into general Windows preamble
    return cdd + '&' + env + '&'


def make_cmd(params, path):
    """
    Constructs a command to set up environment and build
    """
    templates = {
        'cl': Template(
            'cl'
            '{% for source in params["source"] %} "{{source}}"{% endfor %}'
            '{% if "shared" in params["flags"] %} /LD{% endif %}'
            '{% if "debug" in params["flags"] %} /Zi{% endif %}'
            '{% for o in params["options"] %} "{{o}}"{% endfor %}'
            '{% for i in params["include"] %} /I"{{i}}"{% endfor %}'
            '{% if "libs" in params %} /link'
            '{% for l in params["libs"] %} /LIBPATH:"{{l}}"{% endfor %}'
            '{% endif %}'
            ' /out:"{{params["out"]}}" '
        ),
        'gcc': Template(
            'gcc'
            '{% if "shared" in params["flags"] %} -shared{% endif %}'
            '{% if "debug" in params["flags"] %} -g{% endif %}'
            '{% for o in params["options"] %} "{{o}}"{% endfor %}'
            '{% for i in params["include"] %} -I"{{i}}"{% endfor %}'
            '{% for l in params["libs"] %} -L"{{l}}"{% endfor %}'
            ' -o "{{params["out"]}}"'
            '{% if "shared" in params["flags"] %} -fPIC{% endif %}'
            '{% for source in params["source"] %} "{{source}}"{% endfor %}'
        ),
        'g++': Template(
            'g++'
            '{% if "shared" in params["flags"] %} -shared{% endif %}'
            '{% if "debug" in params["flags"] %} -g{% endif %}'
            '{% for o in params["options"] %} "{{o}}"{% endfor %}'
            '{% for i in params["include"] %} -I"{{i}}"{% endfor %}'
            '{% for l in params["libs"] %} -L"{{l}}"{% endfor %}'
            ' -o "{{params["out"]}}"'
            '{% if "shared" in params["flags"] %} -fPIC{% endif %}'
            '{% for source in params["source"] %} "{{source}}"{% endfor %}'
        ),
        'nvcc': Template(
            'nvcc'
            '{% if "shared" in params["flags"] %} --shared{% endif %}'
            '{% if "debug" in params["flags"] %} --debug{% endif %}'
            '{% for o in params["options"] %} "{{o}}"{% endfor %}'
            '{% for i in params["include"] %} -I"{{i}}"{% endfor %}'
            '{% for l in params["libs"] %} -L"{{l}}"{% endfor %}'
            ' -o "{{params["out"]}}"'
            '{% for source in params["source"] %} "{{source}}"{% endfor %}'
        ),
    }

    compiler = params['compiler']

    # If the specific compiler is compatible
    if compiler in templates:

        if os.name == 'nt':  # If running on windows
            preamble = win_env(params, path)  #, Add build environment setup to command
        else:  # If not running on windows
            preamble = ''  # No need to preamble

        # Return complete build script
        return preamble + templates[compiler].render(params=params)
        
    # If no compatible compiler is specified, exit the script now
    else:
        print("No template exists for the given compiler. Exiting.")
        sys.exit()


def load_params(path):
    """
    Loads the json file at 'path', adds default params where not given, and parses autoparams.
    Returns a complete dictionary of params
    """
    data = json.load(open(path))

    # Replace empty fields with default data
    for d in DEFAULTS.keys():
        if d not in data.keys():
            data[d] = DEFAULTS[d]

    # Replace autoparams with actual paths
    data = autoparams(data)

    # Convert ambiguous paramaters into a 1-element list
    for p in ["source"]:  # For each parameter that can be either a list or a string
        if type(data[p]) == str:  # If the parameter is a string
            data[p] = [data[p]]  # Convert parameter into a 1-element list

    # Print data
    for k, v in data.items():
        if type(v) == list:
            v = list2string(v, separator='; ')
        print("{0: <10}: {1}".format(k, v))
    print("\n")

    return data


def press(vinyl_path, debug=False):
    """
    Reads vinyl file from path, 
    constructs full build commands for each target architecture, stores them (optional), then runs them.
    """
    # Load json into parameter dictionary
    params = load_params(vinyl_path) 

    # Keep vinyl file directory
    vinyl_dir = os.path.dirname(vinyl_path)


    ### HANDLE BUILD PATH ###

    # Set up and create build path
    out_dir = os.path.dirname(params["out"])  # Path of output file
    out_fil = os.path.basename(params["out"])  # Name of output file

    # If output directory is relative path
    out_dir = utilities.ensure_absolute(out_dir, vinyl_dir)

    # If build path does not exist
    if not os.path.exists(out_dir):  
        # Create build path
        os.makedirs(out_dir) 
    
    # Re-join build path and file name
    params["out"] = os.path.join(out_dir, out_fil) 


    ### HANDLE SOURCE PATHS ###
    for i, src_path in enumerate(params["source"]):
        params["source"][i] = utilities.ensure_absolute(src_path, vinyl_dir)


    ### CREATE BUILD SCRIPT ###

    # Build the build command
    if debug:
        print(params)
    cmd = make_cmd(params, vinyl_dir)

    # If storing the build command, save as a shell script file
    if "keepscript" in params["flags"]:
        # Save build command to file
        if os.name == 'nt':
            fmt = "bat"
        else:
            fmt = "sh"

        if "debug" in params["flags"]:
            basename = "debug"
        else:
            basename = "build"

        file_name = "{}_{}.{}".format(basename, params["arch"], fmt)
        file_path = os.path.join(vinyl_dir, file_name)
        with open(file_path, "w") as file:
            file.write(cmd)

    # Process build command
    subprocess_cmd(cmd)


# GLOBAL VARIABLES
HOST_ARCH = {'64bit': 'x64', '32bit': 'x86'}[platform.architecture()[0]]  # Find host arch, convert to x64/x86 format

# VINYL PARAMETER DEFAULTS
DEFAULTS = {'arch': HOST_ARCH,
            'vcvars_ver': None,
            'out': 'a.out',
            'flags': [],
            'include': [],
            'libs': [],
            'options': []
            }

# AUTO PARAMETERS
AUTOPARAMS = {
    'compiler': {},
    'include': {},
    'libs': {},
}

# COMPILER AUTO-PARAMS
if os.name == 'nt':  # If running on windows
    AUTOPARAMS['compiler']['$C$'] = 'cl'
    AUTOPARAMS['compiler']['$C++$'] = 'cl'
else:
    AUTOPARAMS['compiler']['$C$'] = 'gcc'
    AUTOPARAMS['compiler']['$C++$'] = 'g++'

# PATHS FROM CONFIG
THIS_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(open(os.path.join(THIS_PATH, './config.json')))
VCVARS_PATH = CONFIG["vcvars_path"]

# PATHS FROM PYTHON ENVIRONMENT
PYTHON_PATHS = get_paths()  # Create dictionary of key-paths
if PYTHON_PATHS:
    print("Python found at {}".format(PYTHON_PATHS['data']))
    AUTOPARAMS['include']['$PYTHON$'] = PYTHON_PATHS['include']
    AUTOPARAMS['libs']['$PYTHON$'] = os.path.join(PYTHON_PATHS['data'], 'libs')

# PATHS FROM EXECUTABLES
CUDA_PATH = os.path.dirname(find_executable("nvcc")).split("\\bin")[0]
if CUDA_PATH:
    print("CUDA found at {}".format(CUDA_PATH))
    AUTOPARAMS['include']['$CUDA$'] = os.path.join(CUDA_PATH, 'include')
    AUTOPARAMS['libs']['$CUDA$'] = os.path.join(CUDA_PATH, 'lib', HOST_ARCH)
    
# PATHS FROM PYTHON IMPORTS
try:
    import numpy
except ImportError:
    pass
else:
    print("Numpy includes found")
    AUTOPARAMS['include']['$NUMPY$'] = os.path.join(numpy.get_include(), 'numpy')
