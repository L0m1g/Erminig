import errno
import os
import subprocess

from . import config


class Rekipe:
    """
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
