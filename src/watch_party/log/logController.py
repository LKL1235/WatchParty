import logging

def init_log_format():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d"
    logging.basicConfig(format=log_format)
    
