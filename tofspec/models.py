#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import h5py
from regex import P
import yaml
import click
from itertools import chain

from .integrate import *
from .utils import *

class TOFSpec(object):
    """
    TOFSpec is a class for wrangling PTR-TOF-MS data, and generating
    labeled time-series datasets that are useful for analyzing data, 
    visualizing data, building machine learning models, and more.

    :param data: hdf5 filepath (or list of hdf5 filepaths)
    :type data: str or list[str]
    """
    def __init__(self, tof_data, mass_axis, **kwargs):
        self.tof_data = tof_data
        self.mass_axis = mass_axis
        self.timestamps = kwargs.pop('timestamps', None)
        self.metadata = kwargs.pop('metadata', None)

        return

    ## methods for munging and analyzing mass spec data by modifying object properties
    def get_time_series(self, mass, **kwargs):
        """
        Compute the abundance of a certain m/Q value vs time. If input is a single mass (m/Q) value,
        the bin for integration is assumed to have a width of 1. Otherwise, mass should be passed as a tuple
        of the form (mass_lower, mass_upper), and mass_range should be specified as True.
        """
        binsize = kwargs.pop('binsize', 1)
        mass_range = kwargs.pop('mass_range', False)

        if mass_range == False:
            mass_lower = (mass-(binsize/2))
            mass_upper = (mass+(binsize/2))
        else:
            mass_lower = mass[0]
            mass_upper = mass[1]

        indices = find_indices(self.mass_axis, mass_lower, mass_upper)

        tof_time_series = integrate_peak(self.tof_data, self.mass_axis, indices)
        
        return tof_time_series
        
    def get_time_series_df(self, masses, **kwargs):
        """
        Using a list of masses or mass range tuples, create a time series 
        dataframe with a column for every compound in the list. Specify column names with optional
        input names.
        """
        mass_range = kwargs.pop('mass_range', False)
        names = kwargs.pop('names', None)

        time_series_masses = []
        with click.progressbar(masses, label='computing time series data') as bar:
            for m in bar:
                time_series_masses.append(self.get_time_series(m, mass_range=mass_range))

        if names is None:
            for m in masses:
                names.append('m{} abundance'.format(m))

        if self.timestamps is not None:
            names.insert(0, "timestamp")
            time_series_masses.insert(0, self.timestamps)

        time_series_df = pd.DataFrame(dict(zip(names, time_series_masses)))

        if "timestamp" in time_series_df.columns:
            time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'])
            time_series_df = time_series_df.set_index('timestamp', drop=True)

        if self.metadata is not None:
            time_series_df['metadata'] = self.metadata

        return time_series_df

    def time_series_df_from_yaml(self, **kwargs):
        """
        Using the default mass list in the config/mass_list.yml file, create a time series 
        dataframe with a column for every compound in the list
        # """
        # path_to_mass_list = kwargs.pop('path_to_mass_list', self.path_to_mass_list)
        # columns = kwargs.pop('columns', 'mf')
        # compound, ion, self.mf, min, max, center = mass_list_from_dict(read_yaml(path_to_mass_list))
        ion, _, min, max, _, _ = vocdb_from_dict(self.voc_dict)
        self.masses = [list(x) for x in zip(min, max)]

        self.time_series_df = self.get_time_series_df(self.masses, names=ion, mass_range=True)
        
        self.time_series_df = self.time_series_df.sort_index()

        return self.time_series_df

    def metadata_integrate(self, **kwargs):
        non_data = kwargs.pop('non_data', [100,10,98,99])

        #save list of data columns
        cols = list(self.time_series_df.columns)
        cols.remove('metadata')

        # assemble the dictionary for aggregating 
        # 1. sum the data columns
        # 2. take the mean time during sampling run
        # 3. keep same metadata
        col_dict = {i:np.sum for i in cols}
        agg_dict = {'timestamp':np.mean,
                    'metadata': np.median,}
        agg_dict.update(col_dict)

        #group by metadata
        g = self.time_series_df.groupby(by='metadata')

        #filter non data values, we only care about probe measurements
        real_data = self.time_series_df.metadata.unique()
        real_data = list(set(real_data) - set(non_data))

        groups = []
        # for each probe
        for i in real_data:
            subgroup = g.get_group(i)
            #sort by time
            subgroup = subgroup.sort_index()
            #check for gaps -- integrate individual sampling runs
            subgroup[1] = subgroup.index.to_series().diff()
            subgroup[1] = subgroup[1] > timedelta(seconds=5) #more than 5 second break means new sampling scheme
            subgroup[1] = subgroup[1].cumsum()
            subgroup.reset_index(inplace=True)

            #do the integration -- sum over observations, take the mean time of the sampling run 
            subgroup = subgroup.groupby(1).agg(agg_dict)
            #reset index
            subgroup.set_index('timestamp', inplace=True)

            groups.append(subgroup)

        integrated_df = pd.concat(groups)

        integrated_df.sort_values('timestamp', inplace=True)

        return integrated_df

    def group_time_series_df(self, **kwargs):
        """
         based on the groups listed in the config/voc-db.yml file,
         sum the time series dataframe to have those groups as columns
        """
        ion, smiles, min, max, center, groups = vocdb_from_dict(self.voc_dict)

        group_list = set(chain(*groups))

        #get all of the compounds in each group
        groups_smiles_dict = {}
        for f in group_list:
            groups_smiles_dict[f] = {'ions': [],}
            for ion in self.voc_dict['ions']:
                if f in ion['groups']:
                    groups_smiles_dict[f]['ions'].append(ion['ion-name'])

        #build grouped dataframe
        self.grouped_df = pd.DataFrame()
        self.grouped_df.index = self.time_series_df.index
        self.grouped_df['metadata'] = self.time_series_df['metadata']

        for group in groups_smiles_dict.keys():
            self.grouped_df[group] = self.time_series_df[groups_smiles_dict[group]['ions']].sum(axis=1)

        return self.grouped_df

    # def group_time_series_df(self, **kwargs):
    #     """
    #     based on the groups that the user specifies, or by default listed in the config/grouping.yml file,
    #     sum the time series dataframe to have those groups as columns
    #     """
    #     #if user inputs a list of groups
    #     groups = kwargs.pop('groups', self.groups)
    #     if set(groups).issubset(self.possible_groups):
    #         pass
    #     else:
    #         groups = self.groups

    #     #get all of the compounds SMILES for each group
    #     groups_smiles_dict = {}
    #     for f in groups:
    #         groups_smiles_dict[f] = {'smiles': [],}
    #         for compound in self.voc_dict:
    #             if f in compound['groups']:
    #                 groups_smiles_dict[f]['smiles'].append(compound['smiles'])

    #     #build grouped dataframe
    #     self.grouped_df = pd.DataFrame()
    #     self.grouped_df.index = self.time_series_df.index
    #     self.grouped_df['metadata'] = self.time_series_df['metadata']

    #     for group in groups_smiles_dict.keys():
    #         self.grouped_df[group] = self.time_series_df[groups_smiles_dict[group]['smiles']].sum(axis=1)

    #     return self.grouped_df