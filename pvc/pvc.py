# -*- coding: utf-8 -*-
import json
import numpy
from sysconfig import get_paths
import os
import platform
import subprocess
import sys
import logging
from jinja2 import Template
from copy import copy


# GLOBAL VARIABLES
HOST_ARCH = {'64bit': 'x64', '32bit': 'x86'}[platform.architecture()[0]]  # Find host arch, convert to x64/x86 format

# PATH SETTINGS
PYTHON_PATHS = get_paths()  # Create dictionary of key-paths
PYTHON_PATHS['libs'] = os.path.join(PYTHON_PATHS['data'], 'libs')  # Add c libraries to paths

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(open(os.path.join(THIS_PATH, './config.json')))

VCVARS_PATH = CONFIG["vcvars_path"]
CUDA_PATH = CONFIG["cuda_path"]
    
# VINYL PARAMETER DEFAULTS
DEFAULTS = {'arch': [HOST_ARCH],
            'vcvars_ver': None,
            'out': 'a.out',
            'flags': [],
            'include': [],
            'libs': [],
            'options': []
            }

# AUTO-PARAMETERS
# Used to add key includes/libs without knowing the path
AUTOPARAMS = {
    'include': {
        '$PYTHON$': PYTHON_PATHS['include'],
        '$NUMPY$': os.path.join(numpy.get_include(), 'numpy'),
        '$CUDA$': os.path.join(CUDA_PATH, 'include')
    },
    'libs': {
        '$PYTHON$': PYTHON_PATHS['libs'],
        '$CUDA$': os.path.join(CUDA_PATH, 'lib', HOST_ARCH)
    },
}

# FUNCTIONS
def list2string(lst, separator=' '):
    """
    Convert a list of strings into a single, space-separated string
    """
    return separator.join(lst)


def subprocess_cmd(command):
    """
    Takes a command as a string, and runs it in a shell process
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].decode()
    print(proc_stdout)


def autoparams(parameter_dictionary):
    """
    Takes a parameter dictionary, and converts autoparam references to their full paths
    """
    global HOST_ARCH
    global AUTOPARAMS

    for section, assignments in AUTOPARAMS.items():  # For each section in AUTOPARAMS
        if section in parameter_dictionary:  # If that section exists in the params dictionary
            parameter_dictionary[section] = [assignments[l] if l in assignments else l for l in
                                             parameter_dictionary[section]]

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
            '{% for o in params["options"] %} "{{o}}"{% endfor %}'
            '{% for i in params["include"] %} /I"{{i}}"{% endfor %}'
            '{% if "libs" in params %} /link'
            '{% for l in params["libs"] %} /LIBPATH:"{{l}}"{% endfor %}'
            '{% endif %}'
            '{% if "debug" in params["flags"] %} /DEBUG{% endif %}'
            ' /out:"{{params["out"]}}" '
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
    for p in ["arch", "source"]:  # For each parameter that can be either a list or a string
        if type(data[p]) == str:  # If the parameter is a string
            data[p] = [data[p]]  # Convert parameter into a 1-element list

    # Print data
    for k, v in data.items():
        if type(v) == list:
            v = list2string(v, separator='; ')
        print("{0: <10}: {1}".format(k, v))
    print("\n")

    return data


def press(path, store_script=True):
    """
    Reads 'vinyl.json' from 'path', 
    constructs full build commands for eachh target architecture, stores them (optional), then runs them.
    """
    if os.path.isfile(os.path.join(path, 'vinyl.json')):  # If vinyl.json exists
        params = load_params(os.path.join(path, 'vinyl.json'))  # Load json into parameter dictionary
    else:
        print("No vinyl file found. Exiting...")
        sys.exit()

    params_modified = copy(params)  # Create a copy of the parameters, for modifying and passing to build build

    # Loop over each build target
    for arch in params["arch"]:  # For each target architecture
        params_modified["arch"] = arch  # Set passed parameter architecture to target

        # Set up and create build path
        build_path = os.path.join(path, "build", params_modified["arch"])  # Calculate build path
        if not os.path.exists(build_path):  # If build path does not exist
            os.makedirs(build_path)  # Create build path
        params_modified["out"] = os.path.join(build_path, params["out"])  # Add build path to output file name

        # Build the build command
        cmd = make_cmd(params_modified, path)

        # TODO: Have this option stored in a vinyl parameter
        # If storing the build command, save as a shell script file
        if store_script:
            # Save build command to file
            if os.name == 'nt':
                fmt = "bat"
            else:
                fmt = "sh"
            file_name = "build_{}.{}".format(arch, fmt)
            file_path = os.path.join(path, file_name)
            with open(file_path, "w") as file:
                file.write(cmd)

        # Process build command
        subprocess_cmd(cmd)
