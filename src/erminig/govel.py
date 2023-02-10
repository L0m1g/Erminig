"""Govel

Forge of Erminig

Usage:
  govel init [--dev | --root | --user] [-v]
  govel --version

Options:
  -h --help            show this help message and exit
  --version            show version and exit
  -v --verbose
"""

""" 
TODO : Add documentation
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


class Govel:
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
        self.arguments = arguments
        self.temporyFile = temporyFile

        if self.arguments["--verbose"]:
            self.log = renablou.Renablou(temporyFile, "debug")
            self.log.debug("Tempory File :" + temporyFile)
        else:
            self.log = renablou.Renablou(temporyFile, "info")

        self.parse_arguments()

    def parse_arguments(self):
        if self.arguments["init"]:
            if self.arguments["--dev"]:
                if os.getuid() != 0:
                    sys.exit()
                self.log.debug("Initialize dev govel")
                self.datas = self.Dev

            elif self.arguments["--root"]:
                if os.getuid() != 0:
                    sys.exit()
                self.log.debug("Initialize root govel")
                self.datas = self.Local

            elif self.arguments["--user"]:
                if os.getuid() == 0:
                    sys.exit()
                self.log.debug("Initialize user govel")
                self.datas = self.User
            else:
                if os.getuid() != 0:
                    self.log.info("Je suppose que vous voulez faire un dépôt utilisateur")
                    self.datas = self.User
            self.initialize()

    def initialize(self):
        """
        TODO : Initialize configuration files
        """
        if os.getuid() == 0:
            self.init_pak_user()
        self.init_folders()
        self.migrate_temporyFile()

    def init_pak_user(self):
        self.create_pak_group()
        self.create_pak_user()

    def init_folders(self):
        for folder in (
            os.path.dirname(self.datas[1]),
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
                    os.path.dirname(folder),
                    pwd.getpwnam(self.datas[0])[2],
                    pwd.getpwnam(self.datas[0])[3],
                    os.stat(os.path.dirname(folder)).st_uid,
                    os.stat(os.path.dirname(folder)).st_gid,
                )

    def check_perms_folder(self, path, uid, gid, r_uid, r_gid):
        if uid != r_uid or gid != r_gid:
            self.log.debug("Changement du propriétaire de " + path)
            os.chown(path, uid, gid)

    def create_pak_user(self):
        """
        TODO : Add message to change password for security purpose
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

    def create_pak_group(self):
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
        shutil.copy(self.temporyFile, self.datas[2])
        if self.arguments["--verbose"]:
            self.log = renablou.Renablou(self.datas[2], "debug")
        else:
            self.log = renablou.Renablou(self.datas[2], "info")
        self.log.debug("Tempory File :" + self.datas[2])


def cli():
    temporyFile = tempfile.mkstemp()[1]
    arguments = docopt(__doc__, version="0.1.0")
    govel = Govel(arguments, temporyFile)
