import io
import os.path
import shutil
import tempfile
import unittest
import zipfile

import sftpzip.localserver

class ZipInMemory:

    @staticmethod
    def tree(root=None):
        root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        for dirpath, dirnames, filenames in os.walk(root):
            for exclude in [".git", "__pycache__"]:
                try:
                    dirnames.remove(exclude)
                except ValueError:
                    pass
            for name in filenames:
                if not name.startswith("."):
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


class ServerTests(NeedsTemporaryDirectory, unittest.TestCase):

    def test_local_server(self):
        #t = sftpzip.localserver.server(self.root)
        pass

class UnzipTests(ZipInMemory, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assertTrue(self.buf.getvalue())
        self.zf = zipfile.ZipFile(self.buf, "r", zipfile.ZIP_DEFLATED, allowZip64=False)

    def test_one(self):
        for info in self.zf.infolist():
            data = self.zf.read(info)
            print(len(data), info)
