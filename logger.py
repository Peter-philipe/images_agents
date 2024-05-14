from logging import LogRecord
import logging
from datetime import datetime
from typing import Union, Generator, Tuple, Callable
import sys
from pathlib import Path
import ast
from functools import wraps
from re import search

num_dir_to_src = 1
src_folder = Path(__file__)
for i in range(num_dir_to_src): src_folder = src_folder.parent

sys.path.insert(0, src_folder.parent.__str__())


# Documentation for logging
# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html
# https://docs.python.org/3/library/logging.html?highlight=logging#logging.basicConfig
# https://docs.python.org/3/library/logging.html?highlight=logging#logrecord-attributes

date_format_standard = '%d/%m/%Y %H:%M:%S %p'
FORMATTER_FOR_CONSOLE = '%(levelname)s - %(asctime)s: %(message)s'
FORMATTER_FOR_FILE = '%(levelname)s (%(name)s) %(asctime)s: %(message)s'
REGEX_FILE_FORMATTER = r"(?:DEBUG|INFO|WARNING|ERROR|CRITICAL|NOTSET|FATAL) \(.+?\) \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM): (.+)"

def create_logger(logger_name: str, file_output: Union[str, Path] = None,
    file_mode: str = "w", without_handler: bool = False) -> logging.Logger:
    """ O nível de criação do logger é ERROR. Deve ser este nível \n
    se você deseja usá-lo como logger raiz e controlar o nível de outros \n
    loggers em sua aplicação. Após a criação, você pode alterar livremente \n
    o nível. \n

    Args:
        `logger_name` (str): Nome do logger
        `file_output` (Union[str, Path], optional): Nome do arquivo de log. \n
        Se especificado, um filehandler é adicionado na criação do logger. O padrão é None.\n
        `file_mode` (str, optional): Modo que o arquivo de log será tratado. Padrão é "w". \n
        `without_handler` (bool, optional): Indicar se o logger teve possuir algum handler. \n
        padrão é False indicando que ele vai herdar os handlers do logger do seu ancestral \n
        `database_log` (bool): Indica se você quer criar um handler para alguma base de dados\n
        `memory_capacity` (int): Capacidade de armazenamento para um MemoryHandler \n

    Returns:
        logging.Logger: logger customizado
    """

    logger = logging.getLogger(logger_name)

    if without_handler: 
        return logger

    if len(logger.handlers) >= 1 and logger_name != "":
        print(f"Já existem handlers para o módulo: {logger_name}")
        print(f"Handlers do módulo: {logger.handlers}")
        return logger
    
    if logger_name == "" and len(logger.handlers) == 0:
        # root logger sem hanlder
        logger.addHandler(make_stremhandler())

    if logger_name == "" and len(logger.handlers) == 1:
        # root logger com handler que não está no formato desejado
        logger.handlers.pop(0)
        logger.addHandler(make_stremhandler())

    if logger_name != "":
        # Não é root logger
        logger.addHandler(make_stremhandler())

    if file_output is not None:
        logger.addHandler(make_filehandler(file_output, file_mode))

    # As menssagens não se propagaram para os loggers ancertrais
    logger.propagate = False
    return logger

def make_stremhandler() -> logging.StreamHandler:

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(FORMATTER_FOR_CONSOLE, datefmt = date_format_standard)
    console_handler.setFormatter(formatter)
    return console_handler

def make_filehandler(file_output: Union[str, Path], file_mode: str = "a",
         files_threshold: int = -1) -> logging.FileHandler:

    if isinstance(file_output, str):
        file_output = Path(file_output)
    
    delete_log_files_until_threshold(file_output.parent, files_threshold)
    file_output = file_output.__str__()

    datetime_in_allow_format = datetime.today().strftime('%d-%m-%y %H-%M-%S.%f')
    file_output = file_output.replace(".log", "-" + datetime_in_allow_format + ".log")

    file_handler = logging.FileHandler(file_output, mode=file_mode)
    formatter = logging.Formatter(FORMATTER_FOR_FILE, datefmt = date_format_standard)
    file_handler.setFormatter(formatter)

    return file_handler

def delete_log_files_until_threshold(folder: Path, threshold: int):

    log_files = tuple(folder.glob("*.log"))
    if len(log_files) >= threshold and threshold > 0:
        _, file_to_remove = min((file.stat().st_mtime, file) for file in log_files)
        file_to_remove.unlink()
        delete_log_files_until_threshold(folder, threshold)


class StreamPersonHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def emit(self, record: LogRecord) -> None:    
        if 'botcity=' in record.msg:
            record.msg = record.msg.split('botcity=')[0].strip()
        

        super().emit(record)


def get_the_last_logs(messages_amount: int = 20, 
                      filter_level: Union[str, Tuple[str]] = None, only_msg: bool = True) -> Tuple:
    """Pegar as últimas menssagens registradas no arquivo .log

    Args:
        `messages_amount` (int, optional): Quantidade de menssagens para recuperar Defaults to 5. \n

        `filter_level` (str, optional): Nível de log que se quer filtrar. Padrão é None \n
        \t Nome dos níveis padrões: \n
        \t 'CRITICAL'; 'FATAL'; 'ERROR'; 'WARN'; 'WARNING'; 'INFO'; 'DEBUG'; 'NOTSET' \n

        `only_msg` (bool, optional): Decidir se quer todo o log ou apenas a messagem principal
    Returns:
        List: Lista de mensagens
    """

    log_file_path = get_log_file()
    last_messages = []
    for item in scan_file_lines(log_file_path):

        last_messages.append(item)
        if len(last_messages) > messages_amount:
            #Evitar o overflow de memória RAM
            last_messages.pop(0)

    if filter_level is not None and isinstance(filter_level, str):
        last_messages = tuple(filter(lambda msg: filter_level in msg, last_messages))

    if filter_level is not None and isinstance(filter_level, tuple):
        temp = []
        for level in filter_level:
            temp.extend(tuple(filter(lambda msg: level in msg, last_messages)))
        last_messages = temp

    if only_msg:
        last_messages = tuple(map(lambda msg: get_only_message_from_file_fomatted_log(msg), last_messages))
    
    return last_messages

def get_log_file()-> Path:
    """Obter arquivo .log atual no qual as messagens de log estão sendo enviadas

    Returns:
        `Path`: Caminho do arquivo .log
    """
        
    for handler in logging.root.handlers:

        if isinstance(handler, logging.FileHandler):

            return Path(handler.baseFilename)
        
    print("Não foi encontrado um FileHandler. Sem ele não é possível ver o histórico de logs")
    return -1



def get_only_message_from_file_fomatted_log(message: str) -> str:
    """Extrair da messagem de log apenas a mensagem principal sem
    a parte de informações de nível, tempo, etc

    Args:
        message (str): Messagem de log

    Returns:
        str: Mensagem principal
    """

    log_file_path = get_log_file()
    message_match = search(REGEX_FILE_FORMATTER, message)

    if message_match is None:

        error_msg = f"Erro ao extrair apenas a messagem do log: {message}"
        with log_file_path.open(mode="a") as log_io: log_io.write(error_msg)
    
        print(error_msg)
        return error_msg
    
    only_msg = message_match.group(1)
    return only_msg


def scan_file_lines(file: Path)-> Generator[str, any, None]:
    """### Ler as linhas do arquivo sem precisar armazenar ele por completo

    Args:
        `file` (Path): Arquivo que vai ser lido

    Yields:
        `Generator`[str, any, None]: String da linha
    """
    with file.open("r") as file_io:
        for line in file_io:
            yield line


def exception_report(_func: Callable = None, *, logmsg: str = None, module_name: str = None):
    """ ## Informar qual foi a exeção que ocorreu de modo mais conciso

    Args:
        `_func` (Callable, optional): Caso não seja passado nenhum argumento-chave\n
        essa variável será a referência da função que será decorada. Se pelo menos \n
        1 argumento-chave por passado essa variável será igual a None \n \n

        `logmsg` (str, optional): Mensagem personalizada para a exeção \n
        `module_name` (str, optional): Módulo com o logger personalizado para emitir a messagem \n
    """

    def decorate_with_log(func):
        wraps(func)
        def wrapper(*args, **kwargs):

            module = module_name if module_name is not None else func.__module__
            logger = logging.getLogger(module)

            msg = logmsg if logmsg is not None else f"Erro na função {func.__name__}"
            
            try:
                value = func(*args, **kwargs)
                return value
            except Exception as error:
                logger.error(msg)
                logger.error(f"Informações sobre erro: {error}")
                raise error

        return wrapper

    if _func is None:
        return decorate_with_log
    else:
        return decorate_with_log(_func)





# Logging config
if __name__ == '__main__': 
    post_danfe_logger = create_logger('')
    post_danfe_logger.setLevel(10)
else: 
    # Nível do log será herdado da raiz
    post_danfe_logger = create_logger(__name__, without_handler = True)

