# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 21:58:52 2017

@author: jtc9242
"""
import os
from argparse import ArgumentParser
from pvc import pvc


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("args",nargs="*")
    a = parser.parse_args()
    
    if len(a.args) > 0: # If the zeroth argument is explicitly given
        PATH = a.args[0]
    else:
        PATH = os.getcwd()

    print("Running in {}".format(PATH))
    pvc.press(PATH)  # Start build process
