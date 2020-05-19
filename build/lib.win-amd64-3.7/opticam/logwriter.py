"""
Module:         log.py

Description:    custom logger class to be able to add color to messages.
"""

#####################################################################################
# Imports
#####################################################################################

import copy
import logging
from termcolor import colored
import colorama


#####################################################################################
# Classes
#####################################################################################

class ColoredFormatter(logging.Formatter):
    """
    Class:          ColoredFormatter

    Description:    Used to format the output.
    """
    COLORS = {
        "INFO": "green",
        "DEBUG": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
        "NOTSET": "white",
        "MSG": "white"
    }
    BACK_COLORS = {
        "INFO": "on_green",
        "DEBUG": "on_blue",
        "WARNING": "on_yellow",
        "ERROR": "on_red",
        "CRITICAL": "on_red",
        "NOTSET": "on_grey",
        "MSG": "on_green"
    }

    def __init__(self, msg, use_color=True):
        """
        Function:       __init__

        Input:          msg (string) - base message
                        use_color (bool) - use color in message

        Output:         None

        Description:    initialise Formater
        """
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        """
        Function:       format

        Input:          record (LogRecord) - object that stores what to display

        Output:         formatted output

        Description:    overridden call to logging.Formatter.format that modifies the message if colors are used.
        """
        levelname = record.levelname
        rec = copy.copy(record)
        if self.use_color:
            levelname_color = colored(levelname, "white", self.BACK_COLORS[levelname])
            rec.levelname = levelname_color
            rec.msg = colored(record.msg, self.COLORS[levelname])
            
        return logging.Formatter.format(self, rec)


class ColoredLogger:
    """
    Class:          ColoredLogger

    Description:    Logger
    """

    LEVEL_MSG = 60 # to be sure it is always printed, put highest level...
    LEVELS = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "NOTSET": logging.NOTSET,
        "MSG": LEVEL_MSG
    }

    def __init__(self, name, filename, level="DEBUG"):
        """
        Function:       __init__

        Input:          name (str) - name of logger

        Output:         None

        Description:    Inject formatter to logger. This is the way to modify text with color.
        """
        colorama.init()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS[level])
        self.file_handler = logging.FileHandler(filename)
        self.file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(self.file_handler)

        logging.addLevelName(self.LEVEL_MSG, "MSG")

    def set_level(self, level):
        if level is not "" and level is not None:
            if level.upper() in self.LEVELS:
                self.logger.setLevel(self.LEVELS[level.upper()])

    def critical(self, message):
        """
        Function:       critical

        Input:          message (str) - message to be displayed

        Output:         None

        Description:    Call logging method. Custom formatter will be used to put color if asked.
        """
        self.logger.critical(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def msg(self, message):
        self.logger.log(msg=message, level=self.LEVEL_MSG)
