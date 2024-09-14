from aiologger.formatters.base import Formatter

class LoggerFormat(Formatter):
    def __init__(self):
        super().__init__(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

formatter = LoggerFormat()