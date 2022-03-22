from vocus import __version__

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import h5py
import yaml
import vocus
import pytest
import unittest

## Should I eventually replace relative filepaths with Github raw user content links

short_data = "tests/datafiles/V3_15s.h5"
long_data = "tests/datafiles/V3_5min.h5"

class TestClass(unittest.TestCase):

    def setUp(self):
        #test load single file
        self.single = vocus.models.Vocus(short_data)

    def test_version(self):
        assert __version__ == '0.1.0'
    
    def test_load(self):
        assert isinstance(self.single, vocus.models.Vocus)
        #test load list of files
        self.multiple = vocus.models.Vocus([short_data, long_data])
        assert isinstance(self.multiple, vocus.models.Vocus)

    def test_data(self):
        #test timestamps length matches tof_data 
        assert self.single.tof_data.shape[0] == len(self.single.timestamps)
        #test tof_data bins length matches mass axis and sum spectrum length
        assert self.single.tof_data.shape[1] == len(self.single.mass_axis)
        assert self.single.tof_data.shape[1] == len(self.single.sum_spectrum)

    def test_config(self):
        #test config files are correct format
        #read in mass list and check
        mass_list_dict = vocus.utils.read_yaml("vocus/config/mass_list.yml")
        self.assertIsInstance(mass_list_dict, dict)
        ion_name, smiles, min, max, center = vocus.utils.ion_lists_from_dict(mass_list_dict)
        self.assertIsInstance(ion_name, list)
        self.assertIsInstance(ion_name[0], str)
        self.assertIsInstance(smiles, list)
        self.assertIsInstance(smiles[0], str)
        self.assertIsInstance(min, list)
        self.assertIsInstance(max, list)
        self.assertIsInstance(center, list)
        
        self.assertGreater(len(ion_name), 0)

        #read in voc db and check
        self.assertIsInstance(self.single.voc_dict, list)

        #check chosen groups is correct format
        self.assertIsInstance(self.single.groups, list)

    def test_integration(self):
        #for these two util tests make sure you get the right answer
        #test find indices in sorted array based on value range
        indices = vocus.integrate.find_indices(self.single.mass_axis, 19,20) 
        self.assertEqual(indices[0], 18668)
        self.assertEqual(indices[1], 19468)

        #test integration of peak
        integrated_peak = vocus.integrate.integrate_peak(self.single.tof_data[6], self.single.mass_axis, indices)
        # make sure the value is between 0.2657 and 0.2659
        ## actual answer should be ~ 0.2658267
        self.assertGreaterEqual(integrated_peak, 0.2657)
        self.assertLessEqual(integrated_peak, 0.2659)

    def test_time_series(self):        
        #test time series df with user input masses
        user_input_df = self.single.get_time_series_df([42, 69, 71], names=['Ethanol', 'Isoprene', 'MVK'])
        self.assertIsInstance(user_input_df, pd.DataFrame)

        #test time series df with masses from mass list
        mass_list_df = self.single.time_series_df_from_yaml()
        self.assertIsInstance(mass_list_df, pd.DataFrame)

        #test grouping yml file is configured correctly (list of chosen groups)
        self.assertGreater(len(self.single.groups), 0)

        #group and sum using chosen groups
        self.single.group_time_series_df()

        self.assertIsInstance(self.single.grouped_df, pd.DataFrame)
        grouped_columns = list(self.single.grouped_df.columns)
        grouped_columns.remove('metadata')
        self.assertEqual(list(self.single.groups), grouped_columns)