"""Govel

Forge of Erminig

Usage:
  govel init [--dev | --root | --user] [-v] [--path PATH]
  govel --version

Options:
  -h --help            show this help message and exit
  --version            show version and exit
  -v --verbose
"""

"""
TODO : add govel add
TODO : add govel delete
TODO : add govel list
TODO : add govel info
TODO : add govel toolchain
TODO : add govel update
TODO : add govel fix
"""

import errno
import os
import pwd
import shutil
import subprocess
import sys
import tempfile

from docopt import docopt

from .lib import renablou
from .lib import users
from .lib import config


class Govel:
    """
    Class to create and use rekipe files, that contain build instructions for the packages.

    There are 4 Level of construction :
    Dev : to create an erminig distribution from a host Linux Distribution
    Global : To maintain a distribution
    Local : to create and maintain independant packages that will be stored in /usr/local
    User : for user-only usage in ~/.local/bin
    ...

    Attributes
    ----------
    arguments : list
        list that contain arguments.
        returned by docopt module
    temporyFile : str
        Log file to use until final log file is created

    Methods
    -------
    def parse_arguments(self):
        Select good datas and parameters to work with

    def initialize(self):
        Create the pak user if necessary
        Create basic folders
        Finalize temporary files

    def init_pak_user(self):
        Create pak user and group

    def init_folders(self):
        Create folders and check permissions

    def check_perms_folder(self, path, uid, gid, r_uid, r_gid):
        Give new permissions if necessary
        A folder created by root can be finally be owned by the pak user

    def create_pak_user(self):
        Create the pak user with a basic password

    def create_pak_group(self):
        Create the pak group

    def migrate_temporyFile(self):
        Copy the temporary logfile in its final destination
    """

    Dev = [
        "pak",
        "/home/pak/erminig",
        "/home/pak/.local/share/govel.log",
        "/home/pak/.config/erminig.conf",
    ]
    Global = ["pak", "/var/lib/erminig", "/var/log/govel.log", "/etc/erminig.conf"]
    Local = [
        "pak",
        "/usr/local/lib/erminig",
        "/usr/local/share/erminig/govel.log",
        "/usr/local/share/erminig/erminig.conf",
    ]
    User = [
        os.environ["USER"],
        os.path.join(os.path.expanduser("~"), ".local/lib/erminig"),
        os.path.join(os.path.expanduser("~"), ".local/share/erminig/govel.log"),
        os.path.join(os.path.expanduser("~"), ".config/erminig.conf"),
    ]

    def __init__(self, arguments, temporyFile):
        """
        Get and check the attributes for the Govel class

        Parameters
        ----------
        arguments : list
            list that contain arguments.
            returned by docopt module
        temporyFile : str
            Log file to use until final log file is created
        """
        self.arguments = arguments
        self.temporyFile = temporyFile

        if self.arguments["--verbose"]:
            self.log = renablou.Renablou(temporyFile, "debug")
            self.log.debug("Tempory File :" + temporyFile)
        else:
            self.log = renablou.Renablou(temporyFile, "info")

        self.parse_arguments()

    def parse_arguments(self):
        """
        Select good datas and parameters to work with
        """
        self.log.debug(self.arguments)
        if self.arguments["init"]:
            if self.arguments["--dev"]:
                if os.getuid() != 0:
                    self.log.error("Must be root")
                    sys.exit()
                self.log.debug("Initialize dev govel")
                self.datas = self.Dev

            elif self.arguments["--root"]:
                if os.getuid() != 0:
                    self.log.error("Must be root")
                    sys.exit()
                self.log.debug("Initialize root govel")
                self.datas = self.Local

            elif self.arguments["--user"]:
                if os.getuid() == 0:
                    self.log.error("Can't be root")
                    sys.exit()
                self.log.debug("Initialize user govel")
                self.datas = self.User
            else:
                if os.getuid() != 0:
                    self.log.info("Je suppose que vous voulez faire un dépôt utilisateur")
                    self.datas = self.User

            if self.arguments["--path"]:
                self.datas[1] = self.arguments["PATH"]
            self.log.debug(self.datas)
            self.initialize()

    def initialize(self):
        """
        Create the pak user if necessary
        Create basic folders
        Finalize temporary files
        """
        if os.getuid() == 0:
            self.init_pak_user()
        self.check_config_file()
        self.init_folders()
        self.migrate_temporyFile()

    def init_pak_user(self):
        """
        Create pak user and group
        """
        self.create_pak_group()
        self.create_pak_user()

    def init_folders(self):
        """
        Create folders and check permissions
        """
        for folder in (
            self.datas[1],
            os.path.dirname(self.datas[2]),
            os.path.dirname(self.datas[3]),
        ):
            try:
                os.makedirs(folder)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    self.log.info(folder + " Already exists")
            finally:
                self.check_perms_folder(
                    folder,
                    pwd.getpwnam(self.datas[0])[2],
                    pwd.getpwnam(self.datas[0])[3],
                    os.stat(folder).st_uid,
                    os.stat(folder).st_gid,
                )

    def check_config_file(self):
        """
        Get config file values
        """
        try:
            self.config = config.Config(self.datas[3])
        except:
            self.log.warn("Error while opening config file")

        if self.arguments["--path"]:
            self.config.set("govel", "path", self.arguments["PATH"])

    def check_perms_folder(self, path, uid, gid, r_uid, r_gid):
        """
        Give new permissions if necessary
        A folder created by root can be finally be owned by the pak user

        Parameters
        ----------
        path : str
            folder to work on
        uid : int
            final uid
        gid : int
            final gid
        r_uid : int
            actual uid
        r_gid : int
            actual gid
        """
        if uid != r_uid or gid != r_gid:
            self.log.debug("Change " + path + " owner")
            os.chown(path, uid, gid)

    def create_pak_user(self):
        """
        Create the pak user with a basic password

        TODO : Add basic bashrc file
        """
        try:
            action = subprocess.run(
                ["useradd", "-k", "/dev/null", "-m", "-r", "-g", "pak", "-p", "pak", "pak"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            action.check_returncode()
        except subprocess.CalledProcessError as e:
            self.log.info(e.stderr.decode("utf-8"))
        else:
            self.log.warn("User pak is created with pak password. Please change it for safety reasons")

    def create_pak_group(self):
        """
        Create the pak group
        """
        try:
            action = subprocess.run(
                ["groupadd", "-r", "pak"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            action.check_returncode()
        except subprocess.CalledProcessError as e:
            self.log.info(e.stderr.decode("utf-8"))

    def migrate_temporyFile(self):
        """
        Copy the temporary logfile in its final destination
        """
        if os.path.exists(self.datas[2]):
            govel = open(self.datas[2], "a+")
            tmp = open(self.temporyFile, "r")
            govel.write(tmp.read())
            govel.seek(0)
            tmp.seek(0)
            govel.close()
            tmp.close()
        else:
            shutil.copy(self.temporyFile, self.datas[2])
            if self.arguments["--verbose"]:
                self.log = renablou.Renablou(self.datas[2], "debug")
            else:
                self.log = renablou.Renablou(self.datas[2], "info")
            self.log.debug("Tempory File :" + self.datas[2])


def cli():
    """
    Function called by the govel executable
    Instance the Govel Class with arguments and temporary file
    """
    temporyFile = tempfile.mkstemp()[1]
    arguments = docopt(__doc__, version="0.1.0")
    govel = Govel(arguments, temporyFile)
