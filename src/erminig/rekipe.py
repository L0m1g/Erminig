import errno
import os
import re
import subprocess

from .lib import config


class Rekipe:
    """
    TODO: Rekipe class is only a lib: Think reusability :)
    class to interact with rekipe files which contain build instruction for packages

    Attributes
    ----------
    arguments : list
        list that contain arguments from govel
    env :
        environment variable from govel

    Methods
    -------
    def add(self)
        add a rekipe file in a category

    def edit(self)
        edit the Rekipe file with $EDITOR

    def get(self, key)
        get value in Rekfile
    """

    env = {}

    def __init__(self, arguments, env):
        self.arguments = arguments
        self.env = env
        self.config = config.Config(self.env["conf"])
        self.rekipe = os.path.join(
            self.env["home"], self.config.get("versions")[0], arguments["CATEGORY"], arguments["PACKAGE"], "Rekipe"
        )
        if arguments["add"]:
            self.add()
        elif arguments["edit"]:
            self.edit()
        elif arguments["info"]:
            self.info()
        elif arguments["fix"]:
            self.fix()
        elif arguments["update"]:
            self.update()

    def add(self):
        """
        Add a rekipe file in a category
        """
        try:
            os.makedirs(os.path.dirname(self.rekipe))
        except:
            print("Existe déjà")
        finally:
            try:
                f = open(self.rekipe, "x")
                f.write(
                    "# Maintainer: Lomig <guillaume.lame@protonmail.com>\n\
\n\
name="
                    + self.arguments["PACKAGE"]
                    + "\n\
description=\n\
\n\
version=\n\
revision=1\n\
\n\
depends=\n\
makedepends=\n\
optdepends=\n\
\n\
url=\n\
basedl=\n\
dl=\n\
\n\
prepare(){\n\
\n\
}\n\
\n\
build(){\n\
\n\
}\n\
\n\
package(){\n\
\n\
}\n\
"
                )
                f.close()
            except OSError as e:
                if e.errno == errno.EEXIST:
                    print("Ça existe déjà Patate")
                    exit(1)
            self.edit()

    def edit(self):
        """
        Edit a rekipe file with $EDITOR
        """
        subprocess.run([os.environ.get("EDITOR"), self.rekipe])

    def info(self):
        """
        Get info for a specific package
        """
        print("Name        : " + self.get("name"))
        print("Description : " + self.get("description"))
        print("Url         : " + self.get("url"))
        print("Version     : " + self.get("version"))
        print("Revision    : " + self.get("revision"))
        print("Download    : " + self.get("dl"))
        print("Depends     : " + self.get("depends"))

    def fix(self):
        """
        Edit a rekipe file by increment revision number
        """
        f = open(self.rekipe, "r")
        data = f.read()
        f.close()
        f = open(self.rekipe, "r")
        lines = f.readlines()
        for line in lines:
            if line.endswith("\n"):
                line = line[:-1]
            array = line.split("=")
            if array[0] == "revision":
                old = "revision=" + array[1]
                new = "revision=" + str(int(array[1]) + 1)
                data = data.replace(old, new)
        f.close()
        f = open(self.rekipe, "w")
        f.write(data)
        f.close()
        self.edit()

    def update(self):
        """
        Update version number in rekfile
        """
        f = open(self.rekipe, "r")
        data = f.read()
        f.close()
        f = open(self.rekipe, "r")
        lines = f.readlines()
        for line in lines:
            array = line.split("=")
            if array[0] == "version":
                flt_old = float(array[1])
                flt_new = float(self.arguments["VERSION"])
                try:
                    flt_old < flt_new
                except:
                    print("La version est plus ancienne que celle déjà utilisée")
                else:
                    old = "version=" + array[1]
                    new = "version=" + self.arguments["VERSION"] + "\n"
                    data = data.replace(old, new)
            if array[0] == "revision":
                print("révision")
                print(array[1])
                old = "revision=" + array[1]
                new = "revision=1" + "\n"
                data = data.replace(old, new)
        f.close()
        f = open(self.rekipe, "w")
        f.write(data)
        f.close()
        self.edit()

    def get(self, key):
        """
        Get value in Rekfile
        """
        f = open(self.rekipe, "r")
        lines = f.readlines()
        for line in lines:
            array = line.split("=")
            if len(array) > 1:
                if array[0] == key:
                    """Traitement des variables bash"""
                    a = re.findall(r"\$\{\w+\}", array[1])
                    if a:
                        for variable in a:
                            v = variable.strip("\$\{")
                            v = v.strip("\}")
                            v = self.get(v)
                            string = array[1]
                            string = string.replace(variable, v)
                            array[1] = string
                    if array[1].startswith("("):
                        a = re.findall(r"\w+", array[1])
                        packages = []
                        for package in a:
                            packages.append(package)
                            packages.sort()

                        l = ""
                        for package in packages:
                            if len(l) > 0:
                                l = l + " " + package
                            else:
                                l = package
                        array[1] = l

                    if array[1].endswith("\n"):
                        value = array[1][:-1]
                    else:
                        value = array[1]

                    value = value.strip('"')
                    value = value.strip("'")
                    value = value.replace("//", "/")
                    return value
