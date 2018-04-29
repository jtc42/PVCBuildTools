# -*- coding: utf-8 -*-
import os

def ensure_absolute(path, basepath):

    # If output directory is relative path
    if not os.path.isabs(path):
        # Join relative build path to vinyl file base path
        out_path = os.path.abspath(os.path.join(basepath, path))
    else:
        out_path = path

    return out_path