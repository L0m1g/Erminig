import os
import subprocess

from . import config


class Rekipe:
    """
    class to interact with rekipe files
    """

    env = {}

    def __init__(self, arguments, env):
        print(env)
        print(arguments)
        self.env = env
        self.config = config.Config(self.env["conf"])
        version = self.config.get("versions")[0]
        self.add(version, arguments["PACKAGE"], arguments["CATEGORY"])

    def add(self, version, package, category):
        try:
            os.makedirs(os.path.join(self.env["home"], version, category, package))
        except:
            print("Existe déjà")
        finally:
            f = open(os.path.join(self.env["home"], version, category, package, "Rekipe"), "x")
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
package(){\n\
\n\
}\n\
"
            )
            f.close()
        subprocess.run([os.environ.get("EDITOR"), os.path.join(self.env["home"], version, category, package, "Rekipe")])
