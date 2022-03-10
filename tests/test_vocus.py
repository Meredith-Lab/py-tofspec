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

class TestClass(unittest.TestCase):

    def test_version():
        assert __version__ == '0.1.0'
    
    def test_load(self):
        short_data = "datafiles/V3_15s.h5"
        long_data = "datafiles/V3_5min.h5"
        #test load single file
        single = vocus.models.Vocus(short_data)
        assert isinstance(single, vocus.models.Vocus)
        #test load list of files
        multiple = vocus.models.Vocus([short_data, long_data])
        assert isinstance(multiple, vocus.models.Vocus)

        #test timestamps length matches tof_data 
        assert single.tof_data.shape[0] == len(single.timestamps)
        #test tof_data bins length matches mass axis and sum spectrum length
        assert single.tof_data.shape[1] == len(single.mass_axis)
        assert single.tof_data.shape[1] == len(single.sum_spectrum)

        # test .copy()
        cpy = single.copy()

        assert isinstance(cpy, vocus.models.Vocus)
        assert cpy != single

        #test config files are correct format
        #read in mass list and check
        mass_list_dict = vocus.utils.read_yaml("../vocus/config/mass_list.yml")
        self.assertIsInstance(mass_list_dict, dict)
        ion_name, smiles, min, max, center = vocus.utils.ion_lists_from_dict(mass_list_dict)
        self.assertIsInstance(ion_name, list)
        self.assertIsInstance(smiles, list)
        self.assertIsInstance(min, list)
        self.assertIsInstance(max, list)
        self.assertIsInstance(center, list)
        
        self.assertGreater(len(ion_name), 0)

        #read in voc db and check
        self.assertIsInstance(single.voc_dict, dict)

        #check chosen groups is correct format
        self.assertIsInstance(single.groups, list)


    def test_time_series(self):
        short_data = "datafiles/V3_15s.h5"
        single = vocus.models.Vocus(short_data)

        #for these two util tests make sure you get the right answer
        #test find indices    

        #test integration


        #test time series with user input masses
        #test time series df with user input masses
        #test time series with masses from mass list
        pass

    def test_grouping(self):
        #test grouping yml file is configured correctly (list of chosen groups)
        #test 
        pass