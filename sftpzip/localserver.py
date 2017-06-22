import argparse
import logging
import os.path
import tempfile
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

def serve(root):
    log = logging.getLogger("localsftp.serve")
    LocalSFTP.root = root

    sock = bind()
    con = listen(sock)
    log.info("Handshaking...")
    t = Transport(con)
    t.set_subsystem_handler("sftp", LocalSFTP)
    log.info("Connecting...")
    t.start_server(server=LocalServer())

def main(args):
    logging.basicConfig()
    log = logging.getLogger("localsftp")
    work_dir = args.work if args.work and os.path.isdir(args.work) else tempfile.mkdtemp()
    log.info("Working from {0}".format(work_dir))
    serve(work_dir)

def parser(description="SFTP server for testing."):
    p = argparse.ArgumentParser(description)
    p.add_argument(
        "--work", default=None,
        help="Set a path to the working directory.")
    return p

if __name__ == "__main__":
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)
