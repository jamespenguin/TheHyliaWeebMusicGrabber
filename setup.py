from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1}},
    console = [{'script': "main.py"}],
    zipfile = None,
    excludes = ['pyreadline', 'difflib', 'doctest', 'locale', 'optparse', 'pickle', 'calendar'],
    name = "AOTK Scrape",
    version = "1.0",
    author = "Penmask",
)
