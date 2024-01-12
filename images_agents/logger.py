import logging
from typing import Union
from pathlib import Path

# Documentation for logging
# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html
# https://docs.python.org/3/library/logging.html?highlight=logging#logging.basicConfig
# https://docs.python.org/3/library/logging.html?highlight=logging#logrecord-attributes

date_format_standard = '%d/%m/%Y %H:%M:%S %p'

def create_logger(logger_name: str, file_output: Union[str, Path] = None, 
    file_mode: str = "w") -> logging.Logger:
    """ ### Generate a logger
    The creation level of the logger is ERROR. It must be this level \n
    if you'd like to use it as root logger and control the level of others\n
    loggers in your application. After the creation, you can change the level freely\n
    
    Args:
        `logger_name` (str): name of the logger \n
        `file_output` (Union[str, Path], optional): path for a file to log. If specified, a filehandler \n
        is added in the creation of the logger. Defaults to None.

    """
    logger = logging.getLogger(logger_name)
 
    if logger.hasHandlers():
        print(f"Handlers for this logger already exists")
        return logger
    
    logger.addHandler(make_stremhandler())

    if file_output is not None:
        logger.addHandler(make_filehandler(file_output, file_mode))

    logger.propagate = False
    return logger
    

def make_stremhandler() -> logging.FileHandler:

    formatter_for_console = '%(levelname)s - %(asctime)s: %(message)s'

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(formatter_for_console, datefmt = date_format_standard)
    console_handler.setFormatter(formatter)
    return console_handler

def make_filehandler(file_output: str, file_mode: str = "a") -> logging.FileHandler:

    if isinstance(file_output, Path):
        file_output = file_output.__str__()

    formatter_for_file = '%(levelname)s (%(name)s) %(asctime)s: %(message)s'
    file_handler = logging.FileHandler(file_output, mode=file_mode)
    formatter = logging.Formatter(formatter_for_file, datefmt = date_format_standard)
    file_handler.setFormatter(formatter)

    return file_handler

def main():
    
    custom_logger = create_logger("borracha", r"rubber_logging.log")
    custom_logger.info("começar")

if __name__ == '__main__':
    main()





