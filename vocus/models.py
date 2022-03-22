#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import h5py
import yaml

from .integrate import *
from .utils import *

class Vocus(object):
    """
    Vocus is a class for wrangling Vocus PTR-TOF-MS data, and generating
    labeled time-series datasets that are useful for analyzing data, 
    visualizing data, building machine learning models, and more.

    :param data: hdf5 filepath (or list of hdf5 filepaths)
    :type data: str or list[str]
    """
    def __init__(self, data, **kwargs):
        # load in Vocus data
        if type(data) is list:
            for i,d in enumerate(data):
                if i == 0:
                    self.timestamps, self.mass_axis, self.sum_spectrum, self.tof_data, self.metadata = self.load_data(d)
                else:
                    timestamps, mass_axis, sum_spectrum, tof_data, metadata = self.load_data(d)
                    self.timestamps = np.concatenate([self.timestamps, timestamps])
                    np.add(self.sum_spectrum, sum_spectrum, out=self.sum_spectrum)
                    self.tof_data = np.concatenate([self.tof_data, tof_data])
                    self.metadata = np.concatenate([self.metadata, metadata])
        else:
            self.timestamps, self.mass_axis, self.sum_spectrum, self.tof_data, self.metadata = self.load_data(data)

        # YAML configuration files contain information for computing time series and functional groups
        self.path_to_mass_list = kwargs.pop('path_to_mass_list', 'vocus/config/mass_list.yml')
        self.path_to_voc_db = kwargs.pop('path_to_voc_db', 'vocus/config/voc_db.yml')

        self.voc_dict = read_yaml(self.path_to_voc_db)['compounds']
        self.possible_groups = read_yaml('vocus/config/grouping.yml')['possible-groups']
        self.groups = read_yaml('vocus/config/grouping.yml')['chosen-groups']

        return

    ## methods for wrangling hdf5 file data and compiling into some properties
    def load_data(self, data):
        """
        extracts useful data from Vocus hdf5 file.
        :param data: hdf5 filepath
        :type data: str
        """
        with h5py.File(data, "r") as f:
            timestamps = self.get_times(f)
            mass_axis = self.get_mass_axis(f)
            sum_spectrum = self.get_sum_spectrum(f)
            tof_data = self.get_tof_data(f, len(timestamps), len(mass_axis))
            metadata = self.get_metadata(f)

        return timestamps, mass_axis, sum_spectrum, tof_data, metadata

    def get_times(self, f):
        """
        extracts array of timestamps that match up with ToF data from Vocus file
        """
        # get experiment start time from log file and transform string to datetime
        start_time = f['AcquisitionLog']['Log']['timestring'][0]
        start_time = datetime.strptime(start_time.decode('UTF-8'), "%Y-%m-%dT%H:%M:%S+00:00")

        # times of observation are recorded as second offsets from start time
        buftimes = np.array(f['TimingData']['BufTimes'])
        
        timestamps = np.array([start_time + timedelta(seconds=i) for i in buftimes.reshape(-1)])
        
        # when the Vocus stops recording measurements, it still finishes out its last five second interval,
        # and records the time of the empty measurements as the start time. This code sets the empty measurement
        # times to NaN
        mask = (timestamps == timestamps[0])
        mask[0] = False

        timestamps[mask] = np.nan

        return timestamps
    
    def get_tof_data(self, f, t, n):
        """
        extracts array of ToF data of shape (t, n) where
        t = number of snapshots that were taken during the experiment, or in other words the number of 
        timesteps (typically seconds) that the experiment was running
        n = number of mass bins that the mass spec is equipped to observe
        """
        tof_data = np.array(f['FullSpectra']['TofData'])
        tof_data = tof_data.reshape(t, n)
        return tof_data

    def get_metadata(self, f):
        """
        returns array of metadata that corresponds to each measurement. 
        The metadata is currently stored in:
        TPS2
        ---> TEMP_INLET target [C]
        by Jordan
        """
        # times of observation are recorded as second offsets from start time
        buftimes = np.array(f['TimingData']['BufTimes'])

        metadata = np.array(f['TPS2']['TwData'])
        metadata_array = np.array(metadata[:, 87])

        return np.repeat(metadata_array, buftimes.shape[1])

    def get_sum_spectrum(self, f):
        """
        returns array that is the sum of all the ToF data taken during the experiment
        """
        sum_spectrum = np.array(f['FullSpectra']['SumSpectrum'])
        return sum_spectrum

    def get_mass_axis(self, f):
        """
        returns array of mass values that the ToF arrays correspond to
        """
        mass_axis = np.array(f['FullSpectra']['MassAxis'])
        return mass_axis

    ## methods for munging and analyzing mass spec data by modifying object properties
    def get_time_series(self, mass, **kwargs):
        """
        Compute the abundance of a certain m/Q value vs time. If input is a single mass (m/Q) value,
        the bin for integration is assumed to have a width of 1. Otherwise, mass should be passed as a tuple
        of the form (mass_lower, mass_upper), and mass_range should be specified as True.
        """
        binsize = 1
        mass_range = kwargs.pop('mass_range', False)

        if mass_range == False:
            mass_lower = (mass-(binsize/2))
            mass_upper = (mass+(binsize/2))
        else:
            mass_lower = mass[0]
            mass_upper = mass[1]

        indices = find_indices(self.mass_axis, mass_lower, mass_upper)

        tof_time_series = integrate_peak(self.tof_data, self.mass_axis, indices)
        # tof_time_series = np.array([(integrate_peak(self.tof_data[i], self.mass_axis, indices)) for i in range(len(self.tof_data))])

        return tof_time_series
        
    def get_time_series_df(self, masses, **kwargs):
        """
        Using a list of masses or mass range tuples, create a time series 
        dataframe with a column for every compound in the list. Specify column names with optional
        input names.
        """
        mass_range = kwargs.pop('mass_range', False)
        names = kwargs.pop('names', None)

        time_series_masses = [self.get_time_series(m, mass_range=mass_range) for m in masses]
        time_series_masses.insert(0, self.timestamps)

        if names == None:
            names = ['timestamp']
            for m in masses:
                names.append('m{} abundance'.format(m))
        else:
            names.insert(0, 'timestamp')

        time_series_df = df_from_arrays(arrays=time_series_masses, names=names)

        time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'])
        time_series_df = time_series_df.set_index('timestamp', drop=True)

        time_series_df['metadata'] = self.metadata

        return time_series_df

    def time_series_df_from_yaml(self):
        """
        Using the default mass list in the config/mass_list.yml file, create a time series 
        dataframe with a column for every compound in the list
        """
        self.ion_name, self.smiles, min, max, center = ion_lists_from_dict(read_yaml(self.path_to_mass_list))
        self.masses = [list(x) for x in zip(min, max)]

        self.time_series_df = self.get_time_series_df(self.masses, names=self.smiles, mass_range=True)

        return self.time_series_df

    def group_time_series_df(self, **kwargs):
        """
        based on the groups that the user specifies, or by default listed in the config/grouping.yml file,
        sum the time series dataframe to have those groups as columns
        """
        #if user inputs a list of groups
        groups = kwargs.pop('groups', self.groups)
        if set(groups).issubset(self.possible_groups):
            pass
        else:
            groups = self.groups

        #get all of the compounds SMILES for each group
        groups_smiles_dict = {}
        for f in groups:
            groups_smiles_dict[f] = {'smiles': [],}
            for compound in self.voc_dict:
                if f in compound['groups']:
                    groups_smiles_dict[f]['smiles'].append(compound['smiles'])

        #build grouped dataframe
        self.grouped_df = pd.DataFrame()
        self.grouped_df.index = self.time_series_df.index
        self.grouped_df['metadata'] = self.time_series_df['metadata']

        for group in groups_smiles_dict.keys():
            self.grouped_df[group] = self.time_series_df[groups_smiles_dict[group]['smiles']].sum(axis=1)

        return self.grouped_df