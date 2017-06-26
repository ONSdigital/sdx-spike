import os

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

