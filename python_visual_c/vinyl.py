# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 21:58:52 2017

@author: jtc9242
"""
import json
import numpy
from sysconfig import get_paths
import os
import re
import platform
import subprocess
import sys
import logging
from jinja2 import Template


# GLOBAL VARIABLES
HOST_ARCH = {'64bit': 'x64', '32bit': 'x86'}[platform.architecture()[0]]

PYTHON_PATHS = get_paths()  # Dictionary of key-paths
PYTHON_PATHS['libs'] = os.path.join(PYTHON_PATHS['data'], 'libs')  # Add c libraries to paths

# VISUAL C SETTINGS
VCVARS = os.path.abspath(
    "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat")

# VINYL DEFAULTS
DEFAULTS = {'arch': HOST_ARCH,
            'out': 'a.out',
            'flags': [],
            'include': [],
            'libs': [],
            'options': []
            }

# AUTO PARAMS
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
def autoparams(parameter_dictionary):
    global AUTOPARAMS

    for section, assignments in AUTOPARAMS.items():  # For each section in AUTOPARAMS
        if section in parameter_dictionary:  # If that section exists in the params dictionary
            parameter_dictionary[section] = [assignments[l] if l in assignments else l for l in
                                             parameter_dictionary[section]]

    return parameter_dictionary


def list2string(lst):
    return ' '.join(lst)


def make_cmd(params):
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
        return templates[compiler].render(params=params)
    else:
        print("No template exists for the given compiler. Exiting.")
        sys.exit()


def load_txt(path):
    with open(path) as f:
        content = f.readlines()

    content = [x.strip() for x in content]  # Remove newlines
    content = [c for c in content if c != '']  # Strip empty lines
    content = [re.split('[=,]', c) for c in content]  # Cut by colon+space (avoids chopping Windows paths)

    # Strip leading and trailing whitespace
    content = [[item.lstrip().rstrip() for item in section] for section in content]

    data = {}
    for c in content:
        if c[1:] != ['']:
            data[c[0]] = c[1:]
        else:
            data[c[0]] = []
    return data


def get_master(path):
    # BUILD ARGUMENT DICTIONARY FROM VINYL FILE
    # ADD MISSING ARGUMENTS FROM 'DEFAULTS' dictionary
    file_name, extension = os.path.splitext(path)

    if extension == ".json":
        data = json.load(open(path))
    else:
        data = load_txt(path)

    for d in DEFAULTS.keys():
        if d not in data.keys():
            data[d] = DEFAULTS[d]

    # Replace autoparams with actual paths
    data = autoparams(data)

    # Print data
    for k, v in data.items():
        print(k, v)

    return data


def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].decode()
    print(proc_stdout)


def press(path):

    if os.path.isfile(os.path.join(path, 'vinyl.json')):
        prs = os.path.join(path, 'vinyl.json')
        print("Pressing from json...")
    elif os.path.isfile(os.path.join(path, 'vinyl.txt')):
        prs = os.path.join(path, 'vinyl.txt')
        print("Pressing from legacy text...")
    else:
        print("No vinyl file found. Exiting...")
        sys.exit()

    dat = get_master(prs)
    cmd = make_cmd(dat)

    if not dat['arch']:
        dat['arch'] = HOST_ARCH

    # TODO: Loop over architectures if a list, otherwise use string as arch
    # TODO: Handle Windows vs Not-Windows better than just printing "NOT WINDOWS"
    if os.name == 'nt':
        cdd = 'SET "VSCMD_START_DIR=""{}"""'.format(path)
        env = 'CALL "' + VCVARS + '" ' + dat['arch']
        command = cdd + '&' + env + '&' + cmd
        print(cmd)
    else:
        print("NOT WINDOWS")
        command = cmd

    subprocess_cmd(command)


if __name__ == "__main__":
    # CMD ARGUMENTS
    try:
        PATH = os.path.abspath(str(sys.argv[1]))
        print("Pressing vinyl from \"{}\"\n".format(PATH))
    except Exception as e:
        logging.exception(e)
        print("No build path given.\n")
        PATH = "./"
        #sys.exit()

    press(PATH)
