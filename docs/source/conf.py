import sys
import os


project = 'Todo project'
copyright = '2023, Filin'
author = 'Filin'


extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


html_theme = "nature"
html_static_path = ["_static"]