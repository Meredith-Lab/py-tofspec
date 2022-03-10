import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import h5py
import yaml

from .integrate import *
from .utils import *

class Vocus(object):
    """
    Vocus is a class for wrangling Vocus PTR-TOF-MS data
    :param data: hdf5 filepath or list of hdf5 filepaths
    :type data: str
    """
    def __init__(self, data, **kwargs):
        if type(data) is list:
            for i,d in enumerate(data):
                if i == 0:
                    self.timestamps, self.mass_axis, self.sum_spectrum, self.tof_data = self.load_data(d)
                else:
                    timestamps, mass_axis, sum_spectrum, tof_data = self.load_data(d)
                    self.timestamps = np.concatenate([self.timestamps, timestamps])
                    np.add(self.sum_spectrum, sum_spectrum, out=self.sum_spectrum)
                    self.tof_data = np.concatenate([self.tof_data, tof_data])
        else:
            self.timestamps, self.mass_axis, self.sum_spectrum, self.tof_data = self.load_data(data)

        self.path_to_mass_list = kwargs.pop('path_to_mass_list', 'config/mass_list.yml')
        self.path_to_voc_db = kwargs.pop('path_to_voc_db', 'config/voc_db.yml')

        self.voc_dict = read_yaml(self.path_to_voc_db)['compounds']
        self.groups = read_yaml('config/grouping.yml')['chosen-groups']

        return

    ## methods for wrangling hdf5 file data and compiling into some properties
    def load_data(self, data):
        with h5py.File(data, "r") as f:
            timestamps = self.get_times(f)
            mass_axis = self.get_mass_axis(f)
            sum_spectrum = self.get_sum_spectrum(f)
            tof_data = self.get_tof_data(f, len(timestamps), len(mass_axis))

        return timestamps, mass_axis, sum_spectrum, tof_data

    def get_times(self, f):
        """
        returns array of timestamps that match up with ToF data
        """
        # get experiment start time from log file and 
        start_time = f['AcquisitionLog']['Log']['timestring'][0]
        start_time = datetime.strptime(start_time.decode('UTF-8'), "%Y-%m-%dT%H:%M:%S+00:00")

        buftimes = np.array(f['TimingData']['BufTimes'])
        
        timestamps = np.array([start_time + timedelta(seconds=i) for i in buftimes.reshape(-1)])
        
        mask = (timestamps == timestamps[0])
        mask[0] = False

        timestamps[mask] = np.nan

        return timestamps
    
    def get_tof_data(self, f, t, n):
        """
        returns array of ToF data of shape (t, n) where
        t = number of snapshots that were taken during the experiment, or in other words the number of 
        timesteps (typically seconds) that the experiment was running
        n = number of mass bins that the mass spec is equipped to observe
        """
        tof_data = np.array(f['FullSpectra']['TofData'])
        tof_data = tof_data.reshape(t, n)
        return tof_data

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
        compute the abundance of a certain m/Q value vs time
        """
        binsize = kwargs.pop('binsize', 1)
        mass_range = kwargs.pop('mass_range', False)

        if mass_range == False:
            mass_lower = (mass-(binsize/2))
            mass_upper = (mass+(binsize/2))
        else:
            mass_lower = mass[0]
            mass_upper = mass[1]

        tof_time_series = np.array([(integrate_peak(self.tof_data[i], self.mass_axis, mass_lower, mass_upper)) for i in range(len(self.tof_data))])

        return tof_time_series
        
    def get_time_series_df(self, masses, **kwargs):
        binsize = kwargs.pop('binsize', 1)
        mass_range = kwargs.pop('mass_range', False)
        names = kwargs.pop('names', None)

        time_series_masses = [self.get_time_series(m, binsize=binsize, mass_range=mass_range) for m in masses]
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

    def group_time_series_df(self):
        """
        based on the groups that the user specifies in the config/grouping.yml file,
        sum the time series dataframe to have those groups as columns
        """
        groups_smiles_dict = {}
        for f in self.groups:
            groups_smiles_dict[f] = {'smiles': [],}
            for compound in self.voc_dict:
                if f in compound['groups']:
                    groups_smiles_dict[f]['smiles'].append(compound['smiles'])

        self.grouped_df = pd.DataFrame()
        self.grouped_df.index = self.time_series_df.index

        for group in groups_smiles_dict.keys():
            self.grouped_df[group] = self.time_series_df[groups_smiles_dict[group]['smiles']].sum(axis=1)

        return self.grouped_df