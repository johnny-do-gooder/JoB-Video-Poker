import logging
import sys
from datetime import datetime

class PokerLogger:
    def __init__(self):
        self.logger = logging.getLogger('poker_game')
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Create file handler
        file_handler = logging.FileHandler(f'poker_game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatters and add them to the handlers
        console_format = logging.Formatter('%(message)s')
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)
        
        # Add the handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        self.logger.debug(f"DEBUG: {message}")
    
    def info(self, message):
        self.logger.info(f"INFO: {message}")
    
    def warning(self, message):
        self.logger.warning(f"WARNING: {message}")
    
    def error(self, message):
        self.logger.error(f"ERROR: {message}")

# Global logger instance
game_logger = PokerLogger()
