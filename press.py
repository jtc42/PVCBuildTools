# -*- coding: utf-8 -*-
import os
import sys
from argparse import ArgumentParser
from pvc import pvc

if __name__ == "__main__":
    parser = ArgumentParser()
    
    # Handle unnamed positional arguments
    parser.add_argument("positional_args",nargs="*")
    args = parser.parse_args()
    
    # If the zeroth argument is explicitly given
    if len(args.positional_args) > 0: 

        print("Using argument for build path...")
        PATH = args.positional_args[0]

        # Convert relative paths to absolute path
        if not os.path.isabs(PATH):
            PATH = os.path.abspath(os.path.join(os.getcwd(), PATH))

        # If file doesn't exist, or isn't specified
        if not os.path.isfile(PATH):  
            print("No valid vinyl file found. Exiting.")
            sys.exit()
        
        print("Running in {}".format(PATH))
        pvc.press(PATH)  # Start build process

    else:
        print("No vinyl file specified. Exiting.")