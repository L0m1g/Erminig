import os
import pwd
import sys

from . import renablou


class UnixUser(object):
    def __init__(self, uid, gid=None):
        self.uid = uid
        self.gid = gid

    def __enter__(self):
        self.cache = os.getuid(), os.getgid()
        if self.gid is not None:
            os.setgid(self.gid)
        os.setuid(self.uid)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.setuid(self.cache[0])
        os.setgid(self.cache[1])


def as_pak_user():
    uid = pak_uid()
    gid = pak_gid()

    print(uid)
    print(gid)

    def wrapper(func):
        def wrapped(*args, **kwargs):
            pid = os.fork()
            if pid == 0:  # we're in the forked process
                if gid is not None:  # GID change requested as well
                    os.setgid(gid)
                os.setuid(uid)  # set the UID for the code within the `with` block
                func(*args, **kwargs)  # execute the function
                os._exit(0)  # exit the child process

        return wrapped

    return wrapper


def pak_uid():
    try:
        pwd.getpwnam("pak")[2]
    except KeyError:
        print("user Pak does not exists")
    finally:
        return pwd.getpwnam("pak")[2]


def pak_gid():
    return pwd.getpwnam("pak")[3]
