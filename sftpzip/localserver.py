import argparse
import socket
import sys

from paramiko.server import ServerInterface
from paramiko.sftp_server import SFTPServer
from paramiko.transport import Transport

"""
See

* https://gist.github.com/lonetwin/3b5982cf88c598c0e169
* https://github.com/rspivak/sftpserver/blob/master/src/sftpserver/stub_sftp.py

"""

class LocalServer(ServerInterface):

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password,publickey"

class LocalSFTP(SFTPServer):

    root = None

def bind(host=None, port=54321):
    host = host or socket.gethostname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    return sock

def listen(sock, fails=12):
    sock.listen(fails)
    con, addr = sock.accept()
    return con

def server(root):
    LocalSFTP.root = root

    sock = bind()
    con = listen(sock)
    t = Transport(con)
    t.set_subsystem_handler("sftp", LocalSFTP)
    t.start_server(server=LocalServer())

    """
    chan = t.accept(timeout=120)
    if chan:
        server = SFTPServer(
            channel=chan,
            name="sftp",
            server=si,
            sftp_si=LocalSFTP
        )
    """

def parser(description="SFTP server for testing."):
    p = argparse.ArgumentParser(description)
    return p

if __name__ == "__main__":
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)
