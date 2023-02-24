"""Govel

Forge of Erminig

Usage:
  govel init (--dev | --global | --local | --user) [-v] [--path PATH]
  govel new (--name NAME) [-v]
  govel add [ --dev | --global | --local | --user] PACKAGE [CATEGORY] [-v]
  govel edit [ --dev | --global | --local | --user] PACKAGE [CATEGORY] [-v]
  govel info [ --dev | --global | --local | --user] PACKAGE [CATEGORY] [-v]
  govel --version

Options:
  -h --help            show this help message and exit
  --version            show version and exit
  -v --verbose
"""

"""
TODO : add govel delete
TODO : add govel list
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
from .lib import config
from . import rekipe


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
    def check_user(self, user):
        Check if script is launch with a specific user

    def environ(self, user, value=None):
        Getter ant Setter for class environment values

     def init_environment(self, env, debug):
        get correct configuration values

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

    def create_pak_folders(self, folders):
        Create folders and give them permissions for pak user

    def new version(self):
        Dispatch all the tasks to create a new version
        A new version can only be created with pak in its home

     def check_config_file(self, section=False, key=False, value=False):
        Get config file values

    def check_perms_folder(self, path, uid, gid, r_uid, r_gid):
        Give new permissions if necessary
        A folder created by root can be finally be owned by the pak user

    def check_user_pak(self):
        Check if pak user is set on the system

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

    env = {}
    Dev = [
        "pak",
        "pak",
        "/home/pak/erminig",
        "/home/pak/.local/share/govel.log",
        "/home/pak/.config/erminig.conf",
    ]
    Global = ["root", "pak", "/var/lib/erminig", "/var/log/govel.log", "/etc/erminig.conf"]
    Local = [
        "root",
        "pak",
        "/usr/local/lib/erminig",
        "/usr/local/share/erminig/govel.log",
        "/usr/local/share/erminig/erminig.conf",
    ]
    User = [
        os.environ["USER"],
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

    def check_user(self, user):
        """
        Check if script is launch with a specific user
        """
        if user == "root":
            if os.getuid() != 0:
                self.log.error("Must be root")
                sys.exit(1)
        elif user == "pak":
            if os.getuid() != pwd.getpwnam("pak")[2]:
                self.log.error("Must be pak")
                sys.exit(1)

    def environ(self, key, value=None):
        """
        Getter ant Setter for class environment values
        """
        if value:
            self.env[key] = value
        else:
            return self.env[key]

    def init_environment(self):
        """
        Check if script is launched with good user and
        get configuration
        """
        if self.arguments["--dev"]:
            self.check_user(self.Dev[0])
            self.populate_environment(self.Dev, "Initialize dev govel")
        elif self.arguments["--global"]:
            self.check_user(self.Global[0])
            self.populate_environment(self.Global, "Initialize global govel")
        elif self.arguments["--local"]:
            self.check_user(self.Local[0])
            self.populate_environment(self.Local, "Initialize local govel")
        elif self.arguments["--user"]:
            self.check_user(self.User[0])
            self.populate_environment(self.User, "Initialize user govel")

    def populate_environment(self, env, debug=None):
        """
        get correct configuration values
        """
        self.log.debug(debug)
        self.environ("check", env[0])
        self.environ("user", env[1])
        self.environ("home", env[2])
        self.environ("log", env[3])
        self.environ("conf", env[4])

    def parse_arguments(self):
        """
        Select good datas and parameters to work with
        """
        if self.arguments["init"]:
            self.init_environment()
            if self.arguments["--path"]:
                self.environ("home", self.arguments["PATH"])
            self.log.debug(self.env)
            self.initialize()
        elif self.arguments["new"]:
            self.check_user(self.Dev[0])
            self.populate_environment(self.Dev)
            self.config = config.Config(self.environ("conf"))
            self.new_version()
        elif self.arguments["add"] or self.arguments["edit"] or self.arguments["info"]:
            if self.arguments["CATEGORY"] == "toolchain":
                self.arguments["--dev"] = True
            elif os.getcwd().startswith("/home/pak"):
                self.arguments["--dev"] = True
            self.init_environment()
            rekipe.Rekipe(self.arguments, self.env)

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
        folders = [
            self.environ("home"),
            os.path.dirname(self.environ("log")),
            os.path.dirname(self.environ("conf")),
        ]
        self.create_pak_folders(folders)

    def create_pak_folders(self, folders):
        """
        Create folders and give them permissions for pak user

        Parameter
        ---------
        folder : list
            Folders to create
        """
        for folder in folders:
            try:
                os.makedirs(folder)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    self.log.info(folder + " Already exists")
                if e.errno == errno.EACCES:
                    self.log.warn("Need to be root")
                    exit(1)
            else:
                self.log.debug(folder + " created")
            finally:
                self.check_perms_folder(
                    folder,
                    pwd.getpwnam(self.environ("user"))[2],
                    pwd.getpwnam(self.environ("user"))[3],
                    os.stat(folder).st_uid,
                    os.stat(folder).st_gid,
                )

    def new_version(self):
        """
        Dispatch all the tasks to create a new version
        A new version can only be created with pak in its home
        """
        self.create_version_folders()
        self.check_config_file(
            "versions", self.arguments["NAME"], os.path.join(self.environ("home"), self.arguments["NAME"])
        )

    def check_config_file(self, section=False, key=False, value=False):
        """
        Get config file values
        """
        try:
            self.config = config.Config(self.environ("conf"))
        except:
            self.log.warn("Error while opening config file")

        if self.arguments["--path"]:
            self.config.set("govel", "path", self.arguments["PATH"])
        else:
            self.config.set("govel", "path", self.environ("home"))

        if key:
            self.config.set(section, key, value)

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
        if os.path.exists(self.environ("log")):
            govel = open(self.environ("log"), "a+")
            tmp = open(self.temporyFile, "r")
            govel.write(tmp.read())
            govel.seek(0)
            tmp.seek(0)
            govel.close()
            tmp.close()
        else:
            shutil.copy(self.temporyFile, self.environ("log"))
            if self.arguments["--verbose"]:
                self.log = renablou.Renablou(self.environ("log"), "debug")
            else:
                self.log = renablou.Renablou(self.environ("log"), "info")
            self.log.debug("Tempory File :" + self.environ("log"))

    def create_version_folders(self):
        """
        Create folders for future development
        """
        if not self.arguments["--name"]:
            self.name = self.give_random_name()
        else:
            self.name = self.arguments["NAME"]
        self.log.debug("name is " + self.name)

        dirname = os.path.join(self.environ("home"), self.name)
        if not os.path.exists(dirname):
            folders = [
                dirname,
                os.path.join(dirname, "toolchain"),
                os.path.join(dirname, "core"),
                os.path.join(dirname, "xorg"),
                os.path.join(dirname, "cli"),
                os.path.join(dirname, "gui"),
            ]
            self.create_pak_folders(folders)

    def give_random_name(self) -> str:
        """
        Give random name if definitive one is not choosed
        TODO: Put 7 better random names
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
