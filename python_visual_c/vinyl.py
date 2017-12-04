# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 21:58:52 2017

@author: jtc9242
"""
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

PYTHON_PATHS = get_paths()  # Create dictionary of key-paths
PYTHON_PATHS['libs'] = os.path.join(PYTHON_PATHS['data'], 'libs')  # Add c libraries to paths

# VISUAL C SETTINGS
VCVARS = os.path.abspath(
    "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat")

# VINYL PARAMETER DEFAULTS
DEFAULTS = {'arch': [HOST_ARCH],
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
    },
    'libs': {
        '$PYTHON$': PYTHON_PATHS['libs'],
    },
}


# FUNCTIONS
def list2string(lst):
    """
    Convert a list of strings into a single, space-separated string
    """
    return ' '.join(lst)


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
    global AUTOPARAMS

    for section, assignments in AUTOPARAMS.items():  # For each section in AUTOPARAMS
        if section in parameter_dictionary:  # If that section exists in the params dictionary
            parameter_dictionary[section] = [assignments[l] if l in assignments else l for l in
                                             parameter_dictionary[section]]

    return parameter_dictionary


def make_cmd(params, path):
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

    if compiler in templates:
        # If running on windows, add build environment setup to command
        if os.name == 'nt':
            cdd = 'SET "VSCMD_START_DIR=""{}"""'.format(path)
            env = 'CALL "' + VCVARS + '" ' + params['arch']
            preamble = cdd + '&' + env + '&'
        else:
            preamble = ''

        return preamble + templates[compiler].render(params=params)
    else:
        print("No template exists for the given compiler. Exiting.")
        sys.exit()


def load_params(path):
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
        print(k, v)

    return data


def press(path, store_script=False):
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
            with open(file_name, "w") as file:
                file.write(cmd)

        # Process build command
        subprocess_cmd(cmd)


if __name__ == "__main__":
    # TODO: Handle lack of path argument nicer than try/except
    try:
        PATH = os.path.abspath(str(sys.argv[1]))  # Get path to build, from shell argument
        print("Pressing vinyl from \"{}\"\n".format(PATH))
    except Exception as e:  # If no path argument was provided
        logging.exception(e)  # Log the error
        print("No build path given.\n")
        sys.exit()

    press(PATH)  # Start build process
