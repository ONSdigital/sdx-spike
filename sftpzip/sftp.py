import argparse
import getpass
import logging
from logging.handlers import WatchedFileHandler
import os.path
import socket
import sys
import zipfile

import paramiko

def unpack(zip_file):
    for info in zip_file.infolist():
        data = zip_file.read(info)
        yield info, data

def transfer(zip_file, user, password, host, port, root, **kwargs):
    t = paramiko.Transport((host, port))
    t.connect(
        hostkey=None,
        username=user,
        password=password,
        gss_host=socket.getfqdn(host),
        gss_auth=False,
        gss_kex=False
    )
    sftp = paramiko.SFTPClient.from_transport(t)
    for info, data in unpack(zip_file):
        if not info.filename.endswith("/"):
            try:
                sftp.putfo(data, info.filename)
            except FileNotFoundError:
                continue
            
        yield info

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
    log = logging.getLogger("sftpclient")

    password = getpass.getpass("Enter password: ")
    kwargs = dict(password=password, **vars(args))
    with zipfile.ZipFile(sys.stdin.buffer) as payload:
        for item in transfer(payload, **kwargs):
            log.info(item)

def parser(description="SFTP client for testing."):
    p = argparse.ArgumentParser(description)
    p.add_argument(
        "--user", default="testuser",
        help="Set the user account for transfer.")
    p.add_argument(
        "--host", default="0.0.0.0",
        help="Set the SFTP host.")
    p.add_argument(
        "--port", type=int, default=22000,
        help="Set the SFTP port.")
    p.add_argument(
        "--root", default="public",
        help="Set the root path for data transfer.")
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
