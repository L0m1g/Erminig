"""Govel

Forge of Erminig

Usage:
  govel init [--dev | --root | --user] [-v] [--path PATH]
  govel add 
  govel new (--name NAME) [-v]
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
TODO : add govel archive
TODO : add govel rename
"""

import errno
import os
import pwd
import random
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

    def create_version_folders(self):
        Create folders for future development

    def give_random_name(self) -> str:
        Give random name if definitive one is not choosed
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

    def check_root(self):
        """
        Check if user is root
        """
        if os.getuid() != 0:
            self.log.error("Must be root")
            sys.exit(1)

    def init_user(self, datas, debug):
        """
        get correct configuration values
        """
        self.log.debug(debug)
        self.datas = datas

    def parse_arguments(self):
        """
        Select good datas and parameters to work with
        """
        self.log.debug(self.arguments)
        if self.arguments["init"]:
            if self.arguments["--dev"]:
                self.check_root()
                self.init_user(self.Dev, "Initialize dev govel")

            elif self.arguments["--root"]:
                self.check_root()
                self.init_user(self.Global, "Initialize root govel")

            elif self.arguments["--user"]:
                self.check_root()
                self.init_user(self.Local, "Initialize user govel")
            else:
                if os.getuid() != 0:
                    self.init_user(self.User, "Je suppose que vous voulez faire un dépôt utilisateur")

            if self.arguments["--path"]:
                self.datas[1] = self.arguments["PATH"]
            self.log.debug(self.datas)
            self.initialize()
        elif self.arguments["new"]:
            self.check_root()
            self.datas = self.Dev
            self.config = config.Config(self.datas[3])
            self.new_version()

    def initialize(self):
        """
        Create the pak user if necessary
        Create basic folders
        Finalize temporary files

        TODO : récupérer la version du système pour l'inclure dans le path
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

    def new_version(self):
        """
        Dispatch all the tasks to create a new version
        A new version can only be created with pak in its home
        """
        self.check_user_pak()
        self.create_version_folders()

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
        else:
            self.config.set("govel", "path", self.datas[1])

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

    def check_user_pak(self):
        """
        Check if pak user is set on the system
        """
        try:
            pwd.getpwnam("pak")
        except KeyError:
            self.log.error("pak user does not exists. Please run govel init before anything else")
            exit(1)

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

    def create_version_folders(self):
        """
        Create folders for future development
        """
        if not self.arguments["--name"]:
            self.name = self.give_random_name()
        else:
            self.name = self.arguments["NAME"]
        self.log.debug("name is " + self.name)

        dirname = os.path.join(self.datas[1], self.name)
        if not os.path.exists(dirname):
            folders = [
                dirname,
                os.path.join(dirname, "toolchain"),
                os.path.join(dirname, "core"),
                os.path.join(dirname, "xorg"),
                os.path.join(dirname, "cli"),
                os.path.join(dirname, "gui"),
            ]
            for folder in folders:
                if not os.path.exists(folder):
                    try:
                        os.makedirs(folder)
                    except OSError as e:
                        if e.errno == errno.EACCES:
                            self.log.warn("Need to be root")
                            exit(1)
                    else:
                        self.log.debug(folder + " created")
                    finally:
                        self.check_perms_folder(
                            folder,
                            pwd.getpwnam(self.datas[0])[2],
                            pwd.getpwnam(self.datas[0])[3],
                            os.stat(folder).st_uid,
                            os.stat(folder).st_gid,
                        )
        else:
            self.log.error("Version " + self.name + " already exists")

    def give_random_name(self) -> str:
        """
        Give random name if definitive one is not choosed
        """
        choices = ["menhir", "dolmen", "tumulus"]
        name = random.choice(choices)
        return name


def cli():
    """
    Function called by the govel executable
    Instance the Govel Class with arguments and temporary file
    """
    temporyFile = tempfile.mkstemp()[1]
    arguments = docopt(__doc__, version="0.1.0")
    govel = Govel(arguments, temporyFile)
