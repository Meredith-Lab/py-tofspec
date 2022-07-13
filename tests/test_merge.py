import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from tofspec.cli import merge

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/datafiles")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_merge_files_csv(self):
        runner = CliRunner()
        result = runner.invoke(merge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        os.path.join(self.test_files_dir, "timeseries.csv"), 
                        os.path.join(self.test_files_dir, "pid.csv"),
                    ],
                    catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

        # are the number of lines correct?
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "timeseries.csv"), index_col=0)
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "pid.csv"), skiprows=3, index_col=0)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[1] + df2.shape[1], df3.shape[1] -1)
