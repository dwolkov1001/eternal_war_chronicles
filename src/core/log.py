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
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Create a file handler to write to game.log (overwrite mode)
    file_handler = logging.FileHandler('game.log', mode='w', encoding='utf-8')
    
    # Create a formatter and set it for both handlers
    # Example format: 2023-10-27 15:04:01,123 - [GAME] - INFO - Your log message
    formatter = logging.Formatter(
        '%(asctime)s - [%(module)s.%(funcName)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add both handlers to the logger
    log.addHandler(console_handler)
    log.addHandler(file_handler) 