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
    # TODO: Handle different types of named argument, as well as unnamed file
    parser.add_argument("args",nargs="*")
    a = parser.parse_args()
    
    if len(a.args) > 0: # If the zeroth argument is explicitly given
        FILE = a.args[0]
        PATH = os.path.dirname(FILE)
    else:
        FILE = "" # Pass no file, so just open Python console
        PATH = os.getcwd()

    # TODO: msvcver as an argument
    params = {'msvcver': 14.11, 'arch': pvc.HOST_ARCH}
    preamble = pvc.win_env(params, PATH)
    
    cmd = preamble + "python {}".format(FILE)
    pvc.subprocess_cmd(cmd)
