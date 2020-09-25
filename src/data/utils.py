import logging

from InfoFilter import InfoFilter


def get_logger(info_log_file, error_log_file_name):
    log = logging.getLogger('default_logger')
    # set console to info
    console_handler = logging.StreamHandler()
    console_handler.addFilter(InfoFilter())
    log.addHandler(console_handler)
    # set info log to info
    file_handler_info = logging.FileHandler(info_log_file, mode='w')
    file_handler_info.addFilter(InfoFilter())
    log.addHandler(file_handler_info)
    # set error log to warn
    file_handler_error = logging.FileHandler(error_log_file_name, mode='w')
    file_handler_error.setLevel(logging.WARNING)
    log.addHandler(file_handler_error)
    log.setLevel(logging.DEBUG)
    return log
