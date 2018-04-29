# -*- coding: utf-8 -*-
import os
import sys
from argparse import ArgumentParser
from pvc import pvc, utilities

if __name__ == "__main__":
    parser = ArgumentParser()
    
    # Handle unnamed positional arguments
    parser.add_argument("positional_args", nargs="*")
    args = parser.parse_args()
    
    # If the zeroth argument is explicitly given
    if len(args.positional_args) > 0: 

        PATH = args.positional_args[0]

        # Convert relative paths to absolute path
        PATH = utilities.ensure_absolute(PATH, os.getcwd())

        # If file doesn't exist, or isn't specified
        if not os.path.isfile(PATH):  
            print("No valid vinyl file found. Exiting.")
            sys.exit()
        
        print("Pressing {}...".format(PATH))
        pvc.press(PATH)  # Start build process

    else:
        print("No vinyl file specified. Exiting.")