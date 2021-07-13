"""Add the two utility packages to the PATH variable, unless they are already in there."""

import os
import sys

# from the location of this file, go up one directory
directory_to_add = os.path.dirname(os.path.realpath(__file__))

# add the directory to PATH
if directory_to_add not in sys.path:
    sys.path.append(directory_to_add)

# now, the three directories "custom_mwclient", "custom_utils", and "bot" can be
# accessed from anywhere in the code
