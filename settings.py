import os
import logging

LOGGING_FORMAT = "%(asctime)s|%(levelname)s: sdx-spike: %(message)s"
LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'DEBUG'))

PORT = int(os.getenv('PORT', 8080))
