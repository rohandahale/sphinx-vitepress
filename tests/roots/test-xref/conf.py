import os

project = "xref"
extensions = ["sphinx.ext.intersphinx"]

# The test points this at a freshly built vpdemo inventory on disk, so the
# "fetch" is a local file read — deterministic and offline.
intersphinx_mapping = {
    "vpdemo": ("https://demo.example/site", os.environ["VPDEMO_INV"]),
}
exclude_patterns = ["_build"]
