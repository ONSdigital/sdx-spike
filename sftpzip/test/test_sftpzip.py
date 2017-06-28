import glob
import io
import os.path
import multiprocessing
import shutil
import tempfile
import time
import unittest
import zipfile

import sftpzip.localserver

from sftpzip.sftp import transfer
from sftpzip.sftp import unpack

class ZipInMemory:

    @staticmethod
    def tree(root=None):
        root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        for dirpath, dirnames, filenames in os.walk(root):
            for node in dirnames[:]:
                if node not in ["sdx-spike", "sftpzip", "test"]:
                    dirnames.remove(node)
            for name in filenames:
                if not name.startswith(".") and not name.endswith(".zip"):
                    yield os.path.join(dirpath, name)

    def setUp(self):
        home = os.path.expanduser("~")
        self.buf = io.BytesIO()
        zf = zipfile.ZipFile(self.buf, "w", zipfile.ZIP_DEFLATED, allowZip64=False)
        with zf as container:
            for fp in self.tree():
                container.write(fp, arcname=fp[len(home):].lstrip(os.sep))
        super().setUp()


class NeedsTemporaryDirectory():

    def setUp(self):
        self.root = tempfile.mkdtemp()
        super().setUp()

    def tearDown(self):
        shutil.rmtree(self.root)


class ServerTests(NeedsTemporaryDirectory, ZipInMemory, unittest.TestCase):

    def test_local_server(self):
        server = multiprocessing.Process(
            target=sftpzip.localserver.serve,
            args=(self.root,)
        )
        server.start()
        time.sleep(5)
        with zipfile.ZipFile(self.buf) as payload:
            for item in transfer(
                payload,
                host="0.0.0.0", port=22000,
                user="testuser", password="",
                root="test"
            ):
                print("transferred ", item)
        self.assertEqual(
            4,
            len(glob.glob(os.path.join(
                self.root, "data", "*", "sdx-spike", "*"
            )))
        )
        self.assertEqual(
            4,
            len(glob.glob(os.path.join(
                self.root, "data", "*", "sdx-spike", "sftpzip", "*"
            )))
        )
        self.assertEqual(
            2,
            len(glob.glob(os.path.join(
                self.root, "data", "*", "sdx-spike", "sftpzip", "test", "*"
            )))
        )
        server.terminate()

class UnzipTests(ZipInMemory, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assertTrue(self.buf.getvalue())
        self.zf = zipfile.ZipFile(self.buf, "r", zipfile.ZIP_DEFLATED, allowZip64=False)

    def test_unpack(self):
        rv = list(unpack(self.zf))
        self.assertEqual(8, len(rv))
        self.assertTrue(all(len(i) == 2 for i in rv))
