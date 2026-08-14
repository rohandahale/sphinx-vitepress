import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "vpdemo"
author = "Rohan Dahale"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

myst_enable_extensions = ["dollarmath"]
napoleon_google_docstring = False
napoleon_numpy_docstring = True

# Tests set VPDEMO_OFFLINE so builds never touch the network.
if os.environ.get("VPDEMO_OFFLINE"):
    intersphinx_mapping = {}
else:
    intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

exclude_patterns = ["_build"]
