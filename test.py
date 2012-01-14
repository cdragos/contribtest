import unittest
import os
import shutil
import random
import string
import generate

from mock import MagicMock, patch
from StringIO import StringIO
from tempfile import NamedTemporaryFile, mkdtemp

INDEX_RST = '{"title": "My awesome site", "layout": "home.html"}\n---\nblah blah'
HOME_HTML = '<h1>{{ title }}</h1>'

class testGenerate(unittest.TestCase):

    @patch("generate.os.listdir")
    def testListFiles(self, mock_listdir):
        mock_listdir.return_value = ["index.rst", "layout"]
        files = list(generate.list_files(""))
        self.assertEqual(files, ["index.rst"])

    @patch("generate.open", create=True)
    def testReadFile(self, mock_open):
        mock_open.return_value = MagicMock(spec=file)
        mock_open.return_value.__enter__.return_value = StringIO(INDEX_RST)

        (metadata, content) = generate.read_file("")
        self.assertIsInstance(metadata, dict)
        self.assertIn("layout", metadata)
        self.assertIsInstance(content, basestring)

    def testGetFileNameOutput(self):
        filename = generate.get_output_filename("test/source/index.rst", "output")
        self.assertEqual(filename, "output/index.html")

    """
    Create temporary files to user for generate_site.
    """
    def testGenerateSite(self):
        tmp_dir = None
        try:
            tmp_dir = "".join(random.choice(string.ascii_lowercase + string.digits)
                                  for x in range(40))
            layout_dir = os.path.join(tmp_dir, "layout")
            os.makedirs(tmp_dir)
            os.makedirs(layout_dir)

            # generate temporary source files
            with open(os.path.join(tmp_dir, "index.rst"), "w+") as index_rst:
                index_rst.write(INDEX_RST)
            with open(os.path.join(layout_dir, "home.html"), "w+") as home_html:
                home_html.write(HOME_HTML)

            generate.generate_site(tmp_dir, tmp_dir)

            # test to see if generated content is expected
            with open(os.path.join(tmp_dir, "index.html"), "r") as index_html:
                content = index_html.read().strip()
                self.assertEqual(content, "<h1>My awesome site</h1>")
        finally:
            # delete temporary directories
            if tmp_dir:
                shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    unittest.main()
