import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd
import numpy as np

from tofspec.cli import integrate_peaks

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/datafiles")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_integrate_peaks_csv(self):
        runner = CliRunner()
        result = runner.invoke(integrate_peaks, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-ts",
                        "timestamp",
                        os.path.join(self.test_files_dir, "test.csv"),
                    ]
                )

        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())


    def test_integrate_peaks_feather(self):
        runner = CliRunner()
        result = runner.invoke(integrate_peaks, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "-ts",
                        "timestamp",
                        "-col=mf",
                        os.path.join(self.test_files_dir, "test.csv"),
                    ]
                )

        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.feather")
        self.assertTrue(p.exists())