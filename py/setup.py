from distutils.core import setup
import py2exe, sys, os
import requests

sys.argv.append('py2exe')

setup(
    version = "0.0.3",
    name = "CMS Extension Service",
    options = {
        'py2exe': {
            'bundle_files': 1,
            'includes': ["urllib.parse.unquote", "requests"],
            'compressed': True,
            "includes": ["sip"],
            'dist_dir': "../bin"
        }
    },
    console = [{
        'script': "server.py"
    }],
    zipfile = None,
    description = "This application acts as a background service for the CMS editor extension that parse and open URLs, download and upload files. ",
    author = "Ze Ran Lu",
    author_email = "zrlu@uwaterloo.ca",
    maintainer = "Ze Ran Lu",
    maintainer_email = "zrlu@uwaterloo.ca"
)

os.remove("../bin/MSVCR100.dll")

