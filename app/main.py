#!/usr/bin/env python3
#   encoding: UTF-8

import argparse
import collections
import logging
import os.path
import signal
import sys

def config():
    variables = [
    "CF_INSTANCE_ADDR",
    "CF_INSTANCE_GUID",
    "CF_INSTANCE_INDEX",
    "CF_INSTANCE_IP",
    "CF_INSTANCE_INTERNAL_IP",
    "CF_INSTANCE_PORT",
    "CF_INSTANCE_PORTS",
    "HOME",
    "MEMORY_LIMIT",
    "PORT",
    "PWD",
    "TMPDIR",
    "USER",
    "VCAP_APP_HOST",
    "VCAP_APP_PORT",
    "VCAP_APPLICATION",
    "VCAP_SERVICES",
    ]
    return collections.ChainMap()

def main(args):
    name = "cf-spike"
    logging.basicConfig(
        format="%(asctime)s |%(levelname)s: {0}: %(message)s".format(name),
        level=args.log_level,
    )
    log = logging.getLogger(name)
    log.info(args)
    return 0

def parser(config, description="SDX service on CF."):
    p = argparse.ArgumentParser(description)
    p.add_argument(
        "--home", default=os.path.abspath(os.getenv("HOME", os.path.dirname(__file__))),
        help="Set a path to the keypair directory."
    )
    p.add_argument(
        "--port", type=int, default=int(os.getenv("PORT", "8080")),
        help="Set a port for the service."
    )
    p.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    p.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    return p


if __name__ == "__main__":
    c = config()
    p = parser(config)
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)
