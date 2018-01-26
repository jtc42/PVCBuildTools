# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
from pvc import pvc

if __name__ == "__main__":
    parser = ArgumentParser()
    
    # Handle named arguments
    parser.add_argument("-vcvars_ver", dest='vcvars_ver', default=None)
    
    # Handle unnamed positional arguments
    parser.add_argument("positional_args",nargs="*")
    
    # Parse all arguments
    args = parser.parse_args()
    
    if len(args.positional_args) > 0: # If the zeroth argument is explicitly given
        FILE = args.positional_args[0] # Grab the file to open in Python
        PATH = os.path.dirname(FILE) # Find the path to start VCVARS in
    else:
        FILE = "" # Pass no file, so just open Python console
        PATH = os.getcwd() # Get current working directory for VCVARS path
        
    if len(args.positional_args) > 1: # If more positional arguments are given
        PYARGS = args.positional_args[1:] # Store them all, to be passed to Python
    else:
        PYARGS = [] # If no extra args are given, just keep an empty list

    # Set up and make preamble command
    params = {'vcvars_ver': args.vcvars_ver, 'arch': pvc.HOST_ARCH}
    preamble = pvc.win_env(params, PATH)
    
    # Create command. Calls preamble, then Python with all supplied arguments
    cmd = preamble + "python {} {}".format(FILE, pvc.list2string(PYARGS))
    
    # Run command
    pvc.subprocess_cmd(cmd)
