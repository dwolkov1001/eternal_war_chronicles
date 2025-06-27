import logging
import sys

# Create a single, shared logger instance
log = logging.getLogger("EternalWarChronicles")
log.setLevel(logging.DEBUG)

# Prevent the logger from propagating messages to the root logger
log.propagate = False

# If the logger already has handlers, don't add more
if not log.handlers:
    # Create a handler to write to the console (stderr by default)
    handler = logging.StreamHandler(sys.stdout)
    
    # Create a formatter and set it for the handler
    # Example format: 2023-10-27 15:04:01,123 - [GAME] - INFO - Your log message
    formatter = logging.Formatter(
        '%(asctime)s - [%(module)s.%(funcName)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add the handler to the logger
    log.addHandler(handler) 