import io
import os.path
import unittest
import zipfile

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
        self.zf = zipfile.ZipFile(self.buf, "w", zipfile.ZIP_DEFLATED, allowZip64=False)
        with self.zf as container:
            for fp in self.tree():
                container.write(fp, arcname=fp[len(home):].lstrip(os.sep))
        super().setUp()


class UnzipTests(ZipInMemory, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assertTrue(self.buf.getvalue())

    def test_one(self):
        pass
