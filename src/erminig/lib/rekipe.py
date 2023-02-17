import errno
import os
import subprocess

from . import config


class Rekipe:
    """
    class to interact with rekipe files
    """

    env = {}

    def __init__(self, arguments, env):
        print(arguments)
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
                    + package
                    + "\n\
description=\n\
\n\
version=\n\
revision=1\n\
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
        subprocess.run([os.environ.get("EDITOR"), self.rekipe])
