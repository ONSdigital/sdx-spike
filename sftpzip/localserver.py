import argparse
import logging
from logging.handlers import WatchedFileHandler
import os.path
import tempfile
import time
import socket
import sys

import paramiko
from paramiko import SFTPAttributes
from paramiko import SFTPHandle
from paramiko.rsakey import RSAKey
from paramiko.server import ServerInterface
from paramiko.sftp_server import SFTPServer
from paramiko.sftp_server import SFTPServerInterface
from paramiko.ssh_exception import PasswordRequiredException
from paramiko.ssh_exception import SSHException
from paramiko.transport import Transport

"""
See

* https://gist.github.com/lonetwin/3b5982cf88c598c0e169
* https://github.com/rspivak/sftpserver/blob/master/src/sftpserver/stub_sftp.py

To test from terminals 1 and 2::

    1: ~/py3.5/bin/python -m sftpzip.localserver -v 
    2: sftp -P 22000 -o PreferredAuthentications=password -o StrictHostKeyChecking=no 127.0.0.1

"""

class LocalServer(ServerInterface):

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password,publickey"

    def check_channel_request(self, kind, chanid):
        log = logging.getLogger("localsftp.session")
        log.info(kind)
        return paramiko.OPEN_SUCCEEDED

class LocalSFTPHandle(SFTPHandle):

    def stat(self):
        try:
            return SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def chattr(self, attr):
        # python doesn't have equivalents to fchown or fchmod, so we have to
        # use the stored filename
        try:
            SFTPServer.set_file_attr(self.filename, attr)
            return paramiko.SFTP_OK
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

class LocalSFTP(SFTPServerInterface):

    home = None

    def canonicalize(self, path):
        return os.path.normpath(os.path.join(self.home, path))

    def start(self):
        log = logging.getLogger("localsftp.service")
        log.info("Started.")
        super().start()

    def list_folder(self, path):
        path = self.canonicalize(path)
        try:
            out = []
            flist = os.listdir(path)
            for fname in flist:
                attr = SFTPAttributes.from_stat(os.stat(os.path.join(path, fname)))
                attr.filename = fname
                out.append(attr)
            return out
        except OSError as e:
            return self.convert_errno(e.errno)

    def stat(self, path):
        path = self.canonicalize(path)
        try:
            return SFTPAttributes.from_stat(os.stat(path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def lstat(self, path):
        path = self.canonicalize(path)
        try:
            return SFTPAttributes.from_stat(os.lstat(path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def mkdir(self, path, attr):
        path = self.canonicalize(path)
        try:
            os.mkdir(path)
            if attr is not None:
                SFTPServer.set_file_attr(path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def chattr(self, path, attr):
        path = self.canonicalize(path)
        try:
            SFTPServer.set_file_attr(path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def open(self, path, flags, attr):
        path = self.canonicalize(path)
        try:
            binary_flag = getattr(os, "O_BINARY",  0)
            flags |= binary_flag
            mode = getattr(attr, "st_mode", None)
            if mode is not None:
                fd = os.open(path, flags, mode)
            else:
                # os.open() defaults to 0777 which is
                # an odd default mode for files
                fd = os.open(path, flags, 0o666)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        if (flags & os.O_CREAT) and (attr is not None):
            attr._flags &= ~attr.FLAG_PERMISSIONS
            SFTPServer.set_file_attr(path, attr)
        if flags & os.O_WRONLY:
            if flags & os.O_APPEND:
                fstr = "ab"
            else:
                fstr = "wb"
        elif flags & os.O_RDWR:
            if flags & os.O_APPEND:
                fstr = "a+b"
            else:
                fstr = "r+b"
        else:
            # O_RDONLY (== 0)
            fstr = "rb"
        try:
            f = os.fdopen(fd, fstr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

        fobj = LocalSFTPHandle(flags)
        fobj.filename = path
        fobj.readfile = f
        fobj.writefile = f
        return fobj

def bind(host=None, port=22000):
    host = host or socket.gethostname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    return sock

def listen(sock, fails=12):
    sock.listen(fails)
    con, addr = sock.accept()
    return con

def get_key(locn):
    log = logging.getLogger("localsftp.keys")
    fp = os.path.join(locn, "id_rsa")
    try:
        key = RSAKey.from_private_key_file(fp)
    except (IOError, PasswordRequiredException, SSHException):
        key = RSAKey.generate(2048)
        key.write_private_key_file(fp)
    return key

def serve(root, interval=12):
    log = logging.getLogger("localsftp.server")
    home = os.path.join(root, "data")
    os.mkdir(home)
    LocalSFTP.home = home

    rv = 0
    log.info("Working from {0}".format(root))
    key = get_key(root)
    log.info("Host key: {0}".format(key.get_base64()))
    try:
        sock = bind()
        log.info("Listening...")
        con = listen(sock)
        log.info("Handshaking...")
        s = LocalServer()
        t = Transport(con)
        t.add_server_key(key)
        t.set_subsystem_handler("sftp", SFTPServer, LocalSFTP)
        log.info("Connecting...")
        t.start_server(server=s)
        chan = t.accept(60)
        if chan is None:
            rv = 1
        else:
            log.info("Serving...")
            while t.is_active():
                time.sleep(interval)
                log.info("Heartbeat.")
    except SSHException as e:
        log.error(e)
        rv = 1
    finally:
        log.info("Stopped.")
        return rv

def main(args):
    log = logging.getLogger("localsftp")
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

    work_dir = args.work if args.work and os.path.isdir(args.work) else tempfile.mkdtemp()
    return serve(work_dir)

def parser(description="SFTP server for testing."):
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
