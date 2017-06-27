import argparse
import logging
from logging.handlers import WatchedFileHandler
import os.path
import sys

def unpack(zip_file):
    for info in zip_file.infolist():
        data = zip_file.read(info)
        print(info)
        yield info, data

class SFTP:

    @staticmethod
    def operations(locn, home=".", mkdirs=False):
        """
        Returns a sequence of commands to copy a file tree from local 'locn' to server 'home'.

        """
        rv = []
        pos = len(locn.split(os.sep))
        for n, (root, dirs, files) in enumerate(os.walk(locn)):
            # We are walking the local file tree
            if n == 0:
                rv.append("cd {0}\n".format(home))
                crumbs = []
            else:
                crumbs = [".."] * (len(root.split(os.sep)) - pos)

            # Navigate to the same spot remotely
            dest = root.split(os.sep)[pos:]
            if dest:
                rv.append("cd {0}\n".format(os.path.join(*dest)))

            if mkdirs:
                rv.extend(["mkdir {0}\n".format(os.path.basename(i)) for i in dirs])

            # Place files
            rv.extend(["put {0}\n".format(os.path.join(root, i)) for i in files])

            # Go back to the home location
            if crumbs:
                rv.append("cd {0}\n".format(os.path.join(*crumbs)))

        return rv

    @staticmethod
    def transfer(cmds, user, host, port, privKey=None, quiet=True):
        """
        Connects to an sftp server and plays a sequence of commands.

        """
        pass


def main(args):
    log = logging.getLogger("sftpclient")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)
    log = logging.getLogger("paramiko")
    log.setLevel(args.log_level)
    log.addHandler(ch)

def parser(description="SFTP client for testing."):
    p = argparse.ArgumentParser(description)
    p.add_argument(
        "--work", default=None,
        help="Set a path to the working directory.")
    p.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    p.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    return p

if __name__ == "__main__":
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)
