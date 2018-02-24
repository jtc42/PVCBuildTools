# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
from pvc import pvc

if __name__ == "__main__":
    parser = ArgumentParser()
    
    # Handle unnamed positional arguments
    parser.add_argument("positional_args",nargs="*")
    args = parser.parse_args()
    
    if len(args.positional_args) > 0: # If the zeroth argument is explicitly given
        PATH = args.positional_args[0]
    else:
        PATH = os.getcwd()

    print("Running in {}\n".format(PATH))
    pvc.press(PATH)  # Start build process
