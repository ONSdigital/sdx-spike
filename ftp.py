#!/usr/bin/python

import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer, MultiprocessFTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("ons", "ons", "./download", perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

server = MultiprocessFTPServer(("0.0.0.0", os.getenv('PORT' ,'2021')), handler)
# server = ThreadedFTPServer(("0.0.0.0", os.getenv('PORT','2021')), handler)
# server = FTPServer(("0.0.0.0", os.getenv('PORT', '2021')), handler)
server.max_cons = 4000
server.serve_forever()
