from inspect import getframeinfo, stack
import os
from datetime import datetime


class Renablou:
    """
    A log/debug class -- renablou is the breton word for log

    There are 6 level of log - name(index):
        - trace(0)
        - debug(1)
        - info(2)
        - warn(3)
        - error(4)
        - fatal(5)

    By instanciate Renablou with one level, you won't see inferior indexed level in terminal,
    but it will be present in logfile.
    ...

    Attibutes
    ---------
    logfile : str
        file to use to store information
    level : str (optional)
        first log level to see in terminal
        if none, the default is info

    Methods
    -------
    int_level(level) -> int
        Return the (int)index of (str)level

     def get_color(type):
        Return the assigned color of the type

    go_log(type, color, caller, message)
        Choose if it has to print log on screen
        Record  log in file

    print_log(type, color, caller, message)
        Print log on screen

    write_log(type, color, caller, message)
        Record  log in file

    def trace(message)
        Generate informations for trace level

    def debug(message)
        Generate informations for debug level

    def info(message)
        Generate informations for info level

    def warn(message)
        Generate informations for warn level

    def error(message)
        Generate informations for error level

    def fatal(message)
        Generate informations for fatal level
    """

    def __init__(self, logfile, level=None):
        """
        Get and check the attributes for the Renablou class

        Parameters
        ----------
        logfile : str
            file to use to store information
        level : str (optional)
            level of log to use
            if none, the default is info
        """
        self.logfile = logfile
        if level is not None:
            self.level = level
        else:
            self.level = "info"

        self.levels = {
            "trace": "\033[37m",
            "debug": "\033[36m",
            "info": "\033[34m",
            "warn": "\033[33m",
            "error": "\033[31m",
            "fatal": "\033[1;31m",
        }
        self.order = self.int_level(self.level)
        self.now = str(datetime.now().time())

    def int_level(self, level) -> int:
        """
        Return the (int)index of(str)level


        Parameters
        ----------
        level : str
            level to choose in the list
        """
        x = 0
        for key, value in self.levels.items():
            if key == level:
                self.order = x
                break
            x += 1

        return x

    def get_color(self, format) -> str:
        """
        return the assigned color of the type

        Parameter
        ---------
        type : str
            log level
        """
        return self.levels[format]

    def go_log(self, type, caller, message):
        """
        Choose if it as to print log on screen
        Record log in file

        Parameters
        ----------
        type : str
            log level
        color : str
            color to choose for the level
        caller : str
            file and line where error occurs
        message : str
            explain of error
        """
        level = self.int_level(type)
        asked = self.int_level(self.level)
        if level >= asked:
            self.print_log(type, caller, message)
        self.write_log(type, caller, message)

    def print_log(self, type, caller, message):
        """
        Print log on screen

        Parameters
        ----------
        type : str
            log level
        color : str
            color to choose for the level
        caller : str
            file and line where error occurs
        message : str
            explain of error
        """
        color = self.get_color(type)
        base = "\033[35m{} " + color + "{} \033[36m{}{} \033[00m{}"
        print(
            base.format(
                self.now + " > ",
                "[ " + type + " ] >",
                os.path.basename(caller.filename) + ":",
                str(caller.lineno) + " > ",
                message,
            )
        )

    def write_log(self, type, caller, message):
        """
        write log in file

        Parameters
        ----------
        type : str
            log level
        color : str
            color to choose for the level
        caller : str
            file and line where error occurs
        message : str
            explain of error
        """
        color = self.get_color(type)
        base = "\033[35m{} " + color + "{} \033[36m{}{} \033[00m{}"
        with open(self.logfile, "a") as f:
            print(
                base.format(
                    self.now + " > ",
                    "[ " + type + " ] >",
                    os.path.basename(caller.filename) + ":",
                    str(caller.lineno) + " > ",
                    message,
                ),
                file=f,
            )

    def trace(self, message):
        """
        Generate informations for trace level

        Parameters
        ----------
        message : str
            message to output
        """
        caller = getframeinfo(stack()[1][0])
        self.go_log("trace", caller, message)

    def debug(self, message):
        """
        Generate informations for debug level

        Parameters
        ----------
        message : str
            message to output
        """
        caller = getframeinfo(stack()[1][0])
        self.go_log("debug", caller, message)

    def info(self, message):
        """
        Generate informations for info level

        Parameters
        ----------
        message : str
            message to output
        """
        caller = getframeinfo(stack()[1][0])
        self.go_log("info", caller, message)

    def warn(self, message):
        """
        Generate informations for warn level

        Parameters
        ----------
        message : str
            message to output
        """
        caller = getframeinfo(stack()[1][0])
        self.go_log("warn", caller, message)

    def error(self, message):
        """
        Generate informations for error level

        Parameters
        ----------
        message : str
            message to output
        """
        caller = getframeinfo(stack()[1][0])
        self.go_log("error", caller, message)

    def fatal(self, message):
        """
        Generate informations for fatal level

        Parameters
        ----------
        message : str
            message to output
        """
        caller = getframeinfo(stack()[1][0])
        self.go_log("fatal", caller, message)
