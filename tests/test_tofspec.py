from tofspec import __version__

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import h5py
import yaml
import tofspec
import pytest
import unittest

## Should I eventually replace relative filepaths with Github raw user content links

short_data = "tests/datafiles/V3_15s.h5"
long_data = "tests/datafiles/V3_5min.h5"

class TestClass(unittest.TestCase):

    def setUp(self):
        self.timestamps, self.mass_axis, self.tof_data, self.metadata = tofspec.load_vocus_data(short_data, metadata=True)

    def test_version(self):
        assert __version__ == '0.1.0'
    
    def test_load(self):
        assert isinstance(self.tof_data, np.ndarray)

    def test_data(self):
        #test timestamps length matches tof_data 
        assert self.tof_data.shape[0] == len(self.timestamps)
        #test tof_data bins length matches mass axis and sum spectrum length
        assert self.tof_data.shape[1] == len(self.mass_axis)
        #test timestamps length matches metadata 
        assert len(self.metadata) == len(self.timestamps)

    def test_config(self):
        #test config file is correct format
        #read in peak-list and check
        peak_list_dict = tofspec.utils.read_yaml("tofspec/config/peak-list.yml")
        self.assertIsInstance(peak_list_dict, dict)
        id, smiles, min, max = tofspec.utils.peak_list_from_dict(peak_list_dict)
        self.assertIsInstance(id, list)
        self.assertIsInstance(id[0], str)
        self.assertIsInstance(smiles, list)
        self.assertIsInstance(smiles[0], str)
        self.assertIsInstance(min, list)
        self.assertIsInstance(max, list)
        
        self.assertGreater(len(id), 0)

    def test_integration(self):
        #for these two util tests make sure you get the right answer
        #test find indices in sorted array based on value range
        indices = tofspec.integrate.find_indices(self.mass_axis, 19,20) 
        self.assertEqual(indices[0], 18668)
        self.assertEqual(indices[1], 19468)

        #test integration of peak
        integrated_peak = tofspec.integrate.integrate_peak(self.tof_data, self.mass_axis, indices)[6]
        # make sure the value is between 0.2657 and 0.2659
        ## actual answer should be ~ 0.2658267
        self.assertGreaterEqual(integrated_peak, 0.2657)
        self.assertLessEqual(integrated_peak, 0.2659)

    def test_time_series(self):        
        #test time series df with user input masses
        user_input_df = tofspec.get_time_series_df(self.tof_data, self.mass_axis, [42, 69, 71], names=['Ethanol', 'Isoprene', 'MVK'])
        self.assertIsInstance(user_input_df, pd.DataFrame)

        #test time series df with masses from mass list
        self.mass_list_df = tofspec.time_series_df_from_yaml(self.tof_data, self.mass_axis, peak_list="tofspec/config/peak-list.yml")
        self.assertIsInstance(self.mass_list_df, pd.DataFrame)

        # #test grouping yml file is configured correctly (list of chosen groups)
        # self.assertGreater(len(self.single.groups), 0)

        # #group and sum using chosen groups
        # self.single.group_time_series_df()

        # self.assertIsInstance(self.single.grouped_df, pd.DataFrame)
        # grouped_columns = list(self.single.grouped_df.columns)
        # grouped_columns.remove('metadata')
        # self.assertEqual(list(self.single.groups), grouped_columns)
    
    def test_lookuptable(self):
        #read in the lookup table
        fx_df = pd.read_feather("tofspec/db/database.feather")
        self.assertIsInstance(fx_df, pd.DataFrame)

    def test_label(self):
        grouped_df = tofspec.group_time_series_df(tofspec.time_series_df_from_yaml(self.tof_data, self.mass_axis, peak_list="tofspec/config/peak-list.yml"), "tofspec/config/peak-list.yml", lookup_table="tofspec/db/database.feather")
        self.assertIsInstance(grouped_df, pd.DataFrame)