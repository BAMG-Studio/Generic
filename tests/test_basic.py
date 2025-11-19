"""Basic tests for ForgeTrace - Author: Peter"""

import shutil
import tempfile
import unittest
from pathlib import Path


class TestForgeTrace(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_import(self):
        """Test that package imports correctly"""
        import forgetrace

        self.assertEqual(forgetrace.__version__, "0.1.0")
        self.assertEqual(forgetrace.__author__, "Peter Kolawole")

    def test_scanners_import(self):
        """Test scanner imports"""
        from forgetrace.scanners import GitScanner, LicenseScanner, SBOMScanner

        self.assertIsNotNone(SBOMScanner)
        self.assertIsNotNone(LicenseScanner)
        self.assertIsNotNone(GitScanner)


if __name__ == "__main__":
    unittest.main()
