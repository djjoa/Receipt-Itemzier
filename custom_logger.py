import logging

class CustomFormatter(logging.Formatter):

    green = "\x1b[32m"
    grey = "\x1b[1;30m"
    # grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # format = "[%(asctime)s] %(name)s:%(levelname)s:  %(message)s (%(filename)s:%(lineno)d)"
    format = "[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
    
# class CustomLogger(CustomFormatter): 
    
#     def __init__(self,  app_name: str ): 
#         self.logger = logging.getLogger(app_name)
        
#         self.logger.setLevel(logging.DEBUG)
#         self.console_handler = logging.StreamHandler()
#         self.console_handler.setLevel(logging.DEBUG)
#         self.console_handler.setFormatter(CustomFormatter())
#         self.logger.addHandler(self.console_handler)

#     def info(self, msg: str):
#         '''wrapper for logger.info'''
#         return self.logger.info(msg)
    
#         '''wrapper for logger.warning'''
#         return self.logger.warning(msg)
    
#     def debug(self, msg: str):
#         '''warpper for logger.debug'''
#         return self.logger.debug(msg)
    
#     def error(self, msg: str):
#         '''wrapper for logger.error'''
#         return self.logger.error(msg) 
    
#     def critical(self, msg: str):
#         '''warpper for logger.critical'''
#         return self.logger.critical(msg) 
        

# log = CustomLogger('walmart')
# log.warn('derp')