# core/logger.py
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file="export_log.txt"):
        self.log_file = log_file
        self.setup_logger()
    
    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def log_export_stats(self, stats):
        self.info(f"Export completed: {stats['written']} written, "
                  f"{stats['skipped']} skipped, {stats['merged']} merged")