import os

import logging
import datetime
import threading

from ropac import system_config as cfg

# 1. DEBUG: Detailed information, typically of interest only when diagnosing problems.
# 2. INFO: Informational messages that highlight the progress of the application at a coarse-grained level.
# 3. WARNING: An indication that something unexpected happened or indicative of some problem in the near future (e.g., ‘disk space low’). The software is still working as expected.
# 4. ERROR: Due to a more serious problem, the software has not been able to perform some function.
# 5. CRITICAL: A very serious error, indicating that the program itself may be unable to continue running.

class Logger:

    def __init__(self, input_name, is_system=False):
        
        logger_name = "{date}_" + os.path.basename(input_name).split('.')[0] + '.log'
        if is_system:
            logger_handler = cfg.system_log_level.output
            logger_level = cfg.system_log_level.level
            logger_dir = os.path.join(cfg.path.logs,'system')
        else:
            logger_handler = cfg.log_level.output
            logger_level = cfg.log_level.level
            logger_dir = os.path.join(cfg.path.logs,os.path.dirname(input_name).split('/')[-1])
        
        if logger_level=='DEBUG':
            level = logging.DEBUG
        elif logger_level=='INFO':
            level = logging.INFO
        elif logger_level=='WARNING':
            level = logging.WARNING
        elif logger_level=='ERROR':
            level = logging.ERROR
        elif logger_level=='CRITICAL':
            level = logging.CRITICAL
        else:
            self.critical("The correct logging level needs to be specified")
            raise ValueError('logger_level should be set to one of the follow: DEBUG, INFO, WARNING, ERROR, or CRITICAL')

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        # Create a log formatter and add it to the file handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(funcName)s - %(message)s')
        log_file_path = os.path.join(logger_dir,logger_name)
        
        if logger_handler=="FILE":
            file_handler = DateRotatingFileHandler(log_file_path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        elif logger_handler=="TERMINAL":
            term_handler = logging.StreamHandler()
            term_handler.setLevel(level)
            term_handler.setFormatter(formatter)
            self.logger.addHandler(term_handler)
            
        elif logger_handler=="BOTH":
            
            file_handler = DateRotatingFileHandler(log_file_path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            term_handler = logging.StreamHandler()
            term_handler.setLevel(level)
            term_handler.setFormatter(formatter)
            self.logger.addHandler(term_handler)
            
        elif logger_handler=="NONE":
            pass
        else:
            self.critical("The correct logging level needs to be specified")
            raise ValueError('logger_level should be set to one of the follow: DEBUG, INFO, WARNING, ERROR, or CRITICAL')

    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)




class DateRotatingFileHandler(logging.FileHandler):
    def __init__(self, filename):
        self.filename = filename
        self.current_date = datetime.date.today()
        self.open_file()
        self.filters = []
        self.lock = threading.RLock()

    def open_file(self):
        filename = self.filename.format(date=self.current_date.strftime("%Y%m%d"))
        if not os.path.exists(os.path.dirname(filename)):    
            os.makedirs(os.path.dirname(filename))
        self.stream = open(filename, mode='a')

    def should_rollover(self, record):
        today = datetime.date.today()
        if today != self.current_date:
            return True
        return False

    def doRollover(self):
        self.stream.close()
        self.current_date = datetime.date.today()
        self.open_file()

       # Define a default filter attribute
    def filter(self, record):
        return True









# # from my_logger import MyLogger

# # logger = MyLogger('my_log_file.txt')
# # logger.info('This is an info message')
# # logger.warning('This is a warning message')
