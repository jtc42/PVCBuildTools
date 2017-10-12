# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 21:58:52 2017

@author: jtc9242
"""

import numpy
from sysconfig import get_paths
import os
import re
import platform
import subprocess
import sys

# ARGUMENTS
try:
    PATH = os.path.abspath(str(sys.argv[1]))
    print("Pressing vinyl from \"{}\"".format(PATH))
except:
    print("No build path given.")
    sys.exit()

# GLOBAL VARIABLES

ARCHS = {'64bit': 'x64', '32bit': 'x86'}
HOST_ARCH = ARCHS[platform.architecture()[0]]

PYTHON_PATHS = get_paths()  # a dictionary of key-paths
PYTHON_PATHS['libs'] = os.path.join(PYTHON_PATHS['data'], 'libs') # add c libraries to paths

            
### BUILD FORMATS ###


FMTS = {'CL':   {'SHAREDLIB':'/MD', 'EXECUTABLE': '/MT'}, 
        'NVCC': {'SHAREDLIB': '--shared', 'EXECUTABLE': ''}
       }

MODE = {'CL':   {'DEBUG': 'd', 'RELEASE': ''},
        'NVCC': {'DEBUG': ' --debug', 'RELEASE': ''}
       }

FLAGS = {'NVCC': {'INCLUDE_DIR': '-I',
                  'LIB_DIR'    : '-L'},
         'CL':   {'INCLUDE_DIR': '/I',
                  'LIB_DIR'    : '/LIBPATH:'}
        }

# CL_SETTINGS
VCVARS = os.path.abspath("C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat")

# VINYL OPTIONS
DEFAULTS = {'COMPILER': ['CL'],
            'ARCHITECTURE': [HOST_ARCH],
            'SOURCE': 'main.c',
            'OUTPUT': 'main.exe',
            'PLATE': [],
            'FORMAT': ['EXECUTABLE', 'RELEASE'],
            'INCLUDE': [],
            'LIBS': [],
            'OPTIONS': []
            }

"""
FORMATS:
    CXX:
    cl <files> <options> <includes> /LINK <linklibs> /out:<output>
    
    CUDA:
    nvcc <options> <includes> <linklibs> -o <output> <files>
    
"""

def list2string(lst):
    return ' '.join(lst)


def make_cmd(compiler, 
             source,
             output,
             plate,
             fmt,
             include,
             libs,
             options):

    
    # HANDLE PLATES
    if 'PYTHON' in plate or 'NUMPY' in plate:
        include.append(PYTHON_PATHS['include'])
        libs.append(PYTHON_PATHS['libs'])
        if not 'SHAREDLIB' in fmt:
            fmt.append('SHAREDLIB')
    # If explicitally numpy, add numpy includes
    if 'NUMPY' in plate:
        include.append(os.path.join(numpy.get_include(), 'numpy'))
        
    # HANDLE OUTPUT EXTENSION
    basename = os.path.splitext(output)[0]
    extension = os.path.splitext(output)[1]
    if 'PYTHON' in plate:
        extension = '.pyd'
    elif 'SHAREDLIB' in fmt:
        extension = '.dll'
    elif extension != '':
        extension = os.path.splitext(output)[1]
    else:
        extension = '.exe'
    
    build_output = basename + extension
    
    
    # HANDLE BUILD FORMAT
    if 'SHAREDLIB' in fmt:
        s = 'SHAREDLIB'
    else:
        s = 'EXECUTABLE'
    if 'DEBUG' in fmt:
        d = 'DEBUG'
    else:
        d = 'RELEASE'
    
    build_format = FMTS[compiler][s] +MODE[compiler][d]

    
    # HANDLE INCLUDES
    build_include = [ FLAGS[compiler]['INCLUDE_DIR'] + f for f in include ] # Build include list
    build_libs    = [ FLAGS[compiler]['LIB_DIR'] + f for f in libs] # Build lib list
    
    # Make command array
    c = []
    if compiler == 'CL':
        c.append('cl') # Compiler
        c.append(list2string(source)) # Source files
        c.append(build_format) # Build format
        c.append(list2string(options)) # Custom options
        c.append(list2string(build_include)) # Includes
        c.append('/link') # Start linker
        c.append(list2string(build_libs)) # Libraries
        c.append('/out:' + build_output) # Output file
        
    elif compiler == 'NVCC':
        c.append('nvcc') # Compiler
        c.append(build_format) # Build format
        c.append(list2string(options)) # Custom options
        c.append(list2string(build_include)) # Includes
        c.append(list2string(build_libs)) # Libraries
        c.append('-o ' + build_output) # Output file
        c.append(list2string(source)) # Source files

    return list2string(c)


#TODO
def get_master(path):
    # BUILD ARGUMENT DICTIONARY FROM VINYL FILE
    # ADD MISSING ARGUMENTS FROM 'DEFAULTS' dictionary
    with open(path) as f:
        content = f.readlines()
    
    content = [x.strip().replace(' ', '') for x in content] # Remove whitespace characters
    #content = [c.split(':') for c in content] # Cut by colon
    content = [re.split(':|,', c) for c in content] # Cut by colon
    
    data = {}
    for c in content:
        if c[1:] != ['']:
            data[c[0]] = c[1:]
        else:
            data[c[0]] = []
    
    for d in DEFAULTS.keys():
        if not d in data.keys():
            data[d] = DEFAULTS[d]
            print("{} NOT FOUND IN VINYL. USING DEFAULT: {}".format(d, DEFAULTS[d]))
    
    print(data)
    return data


def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].decode()
    print(proc_stdout)


def press(path):
    prs = os.path.join(path, 'vinyl.txt')
    dat = get_master(prs)
    
    cmd = make_cmd( dat['COMPILER'][0], dat['SOURCE'], dat['OUTPUT'][0], dat['PLATE'], dat['FORMAT'], dat['INCLUDE'], dat['LIBS'], dat['OPTIONS'] )

    if not dat['ARCHITECTURE']:
        dat['ARCHITECTURE'] = [HOST_ARCH]

    env = "CALL \"" + VCVARS + "\" " + dat['ARCHITECTURE'][0]
    cdd = 'SET "VSCMD_START_DIR=""{}"""'.format(path)
    
    command = cdd + '&' + env + '&' + cmd
    
    subprocess_cmd(command)
    
    

#################################################################### EXAMPLES
#test_path = "D:\Joel\Development\Python scraps\_VINYL_Python Visual C\_TESTS\python_cuda_looper\module"
press(PATH)

"""
#PYTHON MODULE, CUDA
src = ['_pcuda.cpp', 'kernel.cu']
inc = ['./']
lib = []
out = '_pcuda'
plt = ['PYTHON', 'NUMPY']
fmt = []
opt = []

print(make_cmd('NVCC', src, out, plt, fmt, inc, lib, opt))

print('\n\n')

#PYTHON MODULE, CL
src = ['py_artest.cpp']
inc = []
lib = []
out = 'py_artest'
plt = ['PYTHON', 'NUMPY']
fmt = []
opt = []

print(make_cmd('CL', src, out, plt, fmt, inc, lib, opt))
"""