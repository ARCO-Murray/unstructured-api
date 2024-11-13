"""
All environment variable access should be performed via this module.
- allows tracing of where variables are used
- provide sensible defaults
- reduce string typos
"""

import os
import re
import sys

BLOB_ENDPOINT = "http://minio:9000"
BLOB_ACCESS_KEY = "MUST BE SET!"
BLOB_SECRET_KEY = "MUST BE SET!"
BLOB_BUCKET = "documents"

BLOB_URL = "MUST BE SET!"
FILE_NAME = "MUST BE SET!"
CALLBACK_URL = ""
UNSTRUCTURED_COORDINATES = None
UNSTRUCTURED_STRATEGY = None
UNSTRUCTURED_MAX_CHARACTERS = None


def keys():
    # must be all caps or underscores
    return [k for k in globals() if re.match(r"\b[A-Z_]+\b", k)]


# Magic: Override locals with environment settings
for key in dict(locals()):
    if key in os.environ:
        setattr(sys.modules[__name__], key, os.getenv(key))
