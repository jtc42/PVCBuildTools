import sys
import os
import json

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


params = {'include': [],
          'libs': [],
          'flags': []
          }

# Check for NVCC
if query_yes_no("Are you building with CUDA?", default="no"):
    params["compiler"] = "nvcc"
    params["vcvars_ver"] = 14.11
    params["include"].append("$CUDA$")
    params["libs"].append("$CUDA$")
else:
    if os.name == 'nt':
        params["compiler"] = "cl"
    else:
        params["compiler"] = "gcc"

# Check ARCH
if query_yes_no("Are you building for both x86 and x64?", default="no"):
    params["arch"] = ["x64", "x86"]

# Check shared library
if query_yes_no("Are you building a shared library?", default="no"):
    params["flags"].append("shared")

# Check Python
if query_yes_no("Are you building a Python module?", default="no"):
    if not "shared" in params["flags"]:
        params["flags"].append("shared")
    params["include"].append("$PYTHON$")
    params["include"].append("$NUMPY$")
    params["libs"].append("$PYTHON$")

# Add source
src = input("Enter the name of your source file (edit vinyl.json to add more): ")
params["source"] = [src]

# Add source
out = input("Enter the name of your output file: ")
params["out"] = out

with open('vinyl.json', 'w') as fp:
    json.dump(params, fp, indent=2)
    print("Saved vinyl.json to current working directory.\nPlease edit this file for additional options (see readme).")