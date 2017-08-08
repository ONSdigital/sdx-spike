#!/usr/bin/env python3
#   encoding: UTF-8

import argparse
import collections
import json
import logging
import os.path
import signal
import sys

import tornado.ioloop
import tornado.web

__version__ = "0.1.0"

class StatusService(tornado.web.RequestHandler):

    def initialize(self, cfg):
        self.cfg = cfg

    def get(self):
        self.write(dict(self.cfg))


def create_app(cfg):
    return tornado.web.Application([
        ("/health", StatusService, {"cfg": cfg}),
    ])


def shutdown(name, log=None, loop=None):
    loop = loop or tornado.ioloop.IOLoop.current()
    log = log or logging.getLogger("cf-spike")
    log.info("Received shutdown signal.")
    loop.stop()

def config(args):
    env = {k: v for k, v in ((i, os.getenv(i)) for i in (
        "CF_INSTANCE_ADDR", "CF_INSTANCE_GUID", "CF_INSTANCE_INDEX",
        "CF_INSTANCE_IP", "CF_INSTANCE_INTERNAL_IP", "CF_INSTANCE_PORT",
        "CF_INSTANCE_PORTS", "HOME", "MEMORY_LIMIT",
        "PORT", "PWD", "TMPDIR",
        "USER", "VCAP_APP_HOST", "VCAP_APP_PORT")) if v is not None}
    application = json.loads(os.getenv("VCAP_APPLICATION", "{}"))
    services = json.loads(os.getenv("VCAP_SERVICES", "{}"))
    options = dict(vars(args), version=args.version)
    return collections.ChainMap(env, application, services, options)


def main(cfg):
    name = "cf-spike"
    logging.basicConfig(
        format="%(asctime)s |%(levelname)s: {0}: %(message)s".format(name),
        level=cfg["LOG_LEVEL"],
    )
    log = logging.getLogger(name)
    log.info(cfg)

    app = create_app(cfg)
    app.listen(int(cfg["PORT"]))
    loop = tornado.ioloop.IOLoop.current()
    signal.signal(signal.SIGTERM, shutdown)
    loop.start()

    return 0


def parser(description="SDX service on CF."):
    p = argparse.ArgumentParser(description)
    p.add_argument(
        "--home", dest="HOME",
        default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..")),
        help="Set a path to the home directory."
    )
    p.add_argument(
        "--port", dest="PORT", type=int, default=8080,
        help="Set a port for the service."
    )
    p.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="LOG_LEVEL",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output"
    )
    p.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number"
    )
    return p


if __name__ == "__main__":
    rv = 0
    p = parser()
    args = p.parse_args()
    if args.version:
        print(__version__)
    else:
        cfg = config(args)
        rv = main(cfg)
    sys.exit(rv)
