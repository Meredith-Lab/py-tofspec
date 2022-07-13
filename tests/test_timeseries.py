import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd
import numpy as np

from tofspec.cli import timeseries

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/datafiles")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_timeseries(self):
        runner = CliRunner()
        result = runner.invoke(timeseries, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-c",
                        "mf",
                        self.test_files_dir, 
                    ]
                )

        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())