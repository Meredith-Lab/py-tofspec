#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
import rich_click as click
from itertools import chain

from .integrate import *
from .utils import *


def get_time_series(tof_data, mass_axis, mass, **kwargs):
    """
    Compute the abundance of a certain m/Q value vs time. If input is a single mass (m/Q) value,
    the bin for integration is assumed to have a width of 1. Otherwise, mass should be passed as a tuple
    of the form (mass_lower, mass_upper), and mass_range should be specified as True.

    Inputs
    ------
    :param tof_data: matrix of TOF mass spec data. shape = (t,n) where
                t = number of snapshots that were taken during the experiment, or in other words the number of 
                    timesteps (typically seconds) that the experiment was running
                n = number of TOF bins that the mass spec is equipped to observe
    :type tof_data: np.ndarray
    :param mass_axis: array of m/Q values that characterize the TOF bins of the mass spec
    :type mass_axis: np.ndarray
    :param mass: m/Q value to be integrated over (or m/Q range -- see optional args)
    :type mass: float or tuple

    Optional Arguments
    ------------------
    :param binsize: if mass is a single value, the width of the m/Q integration range. (default = 1)
    :type binsize: float
    :param mass_range: if True, then mass should be given as a tuple that gives the lower bound and upper bound
                        of the integration range. (default = False)
    :type mass_range: boolean

    Output
    ------
    :return: time series array of the integrated counts/concentration for the specified m/Q
    :rtype: np.array (shape=(t,))
    """
    binsize = kwargs.pop('binsize', 1)
    mass_range = kwargs.pop('mass_range', False)

    if mass_range == False:
        mass_lower = (mass-(binsize/2))
        mass_upper = (mass+(binsize/2))
    else:
        mass_lower = mass[0]
        mass_upper = mass[1]

    indices = find_indices(mass_axis, mass_lower, mass_upper)

    tof_time_series = integrate_peak(tof_data, mass_axis, indices)
    
    return tof_time_series



def get_time_series_df(tof_data, mass_axis, masses, **kwargs):
    """
    Using a list of masses or mass range tuples, create a time series 
    dataframe with a column for every mass in the list. Options to specify
    column names, supply timestamps and/or metadata.


    Inputs
    ------
    :param tof_data: matrix of TOF mass spec data. shape = (t,n) where
                t = number of snapshots that were taken during the experiment, or in other words the number of 
                    timesteps (typically seconds) that the experiment was running
                n = number of TOF bins that the mass spec is equipped to observe
    :type tof_data: np.ndarray
    :param mass_axis: array of m/Q values that characterize the TOF bins of the mass spec
    :type mass_axis: array-like
    :param masses: list/array of m/Q values to be integrated over (or m/Q range -- see optional args)
    :type mass: array-like (floats or tuples)

    Optional Arguments
    ------------------
    :param binsize: if mass is a single value, the width of the m/Q integration range. (default = 1)
    :type binsize: float
    :param mass_range: if True, then mass should be given as a tuple that gives the lower bound and upper bound
                        of the integration range. (default = False)
    :type mass_range: boolean
    :param names: identifiers for the list of masses provided. could be ions, compounds, or SMILES
    :type names: array-like
    :param timestamps: datetimes that match each row of data in tof_data
    :type timestamps: array-like
    :param metadata: metadata that match each row of data in tof_data
    :type metadata: array-like

    Output
    ------
    :return: dataframe of the integrated counts/concentration for the specified m/Q values
    :rtype: pd.Dataframe
    """
    binsize = kwargs.pop('binsize', 1)
    mass_range = kwargs.pop('mass_range', False)
    names = kwargs.pop('names', None)
    timestamps = kwargs.pop('timestamps', None)
    metadata = kwargs.pop('metadata', None)

    time_series_masses = []
    for m in masses:
        time_series_masses.append(get_time_series(tof_data, mass_axis, m, binsize=binsize, mass_range=mass_range))

    if names is None:
        for m in masses:
            names.append('m{} abundance'.format(m))

    if timestamps is not None:
        names.insert(0, "timestamp")
        time_series_masses.insert(0, timestamps)

    time_series_df = pd.DataFrame(dict(zip(names, time_series_masses)))

    if "timestamp" in time_series_df.columns:
        time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'])
        time_series_df = time_series_df.set_index('timestamp', drop=True)

    if metadata is not None:
        time_series_df['metadata'] = metadata

    return time_series_df


def time_series_df_from_yaml(tof_data, mass_axis, **kwargs):
    """
    Using the default mass list in the config/voc-db.yml file, or one 
    specified by the user, create a time series dataframe with a column for
    every compound in the list.

    Inputs
    ------
    :param tof_data: matrix of TOF mass spec data. shape = (t,n) where
                t = number of snapshots that were taken during the experiment, or in other words the number of 
                    timesteps (typically seconds) that the experiment was running
                n = number of TOF bins that the mass spec is equipped to observe
    :type tof_data: np.ndarray
    :param mass_axis: array of m/Q values that characterize the TOF bins of the mass spec
    :type mass_axis: array-like

    Optional Arguments
    ------------------
    :param peak_list: path to configuration yml file
    :type peak_list: str
    :param timestamps: array of datetimes that match the moments of observation
    :type timestamps: array-like
    :param metadata: array of metadata that match the observations
    :type metadata: array-like

    Output
    ------
    :return: dataframe of the integrated counts/concentration for the specified m/Q values
    :rtype: pd.Dataframe

    """
    timestamps = kwargs.pop('timestamps', None)
    metadata = kwargs.pop('metadata', None)
    peak_list = kwargs.pop('peak_list', 'config/peak-list.yml')
    columns = kwargs.pop('columns', 'smiles')
    voc_dict = read_yaml(peak_list)
    mf, smiles, min, max = peak_list_from_dict(voc_dict)
    if columns == 'mf':
        cols = mf
    else:
        cols = smiles
    masses = [list(x) for x in zip(min, max)]

    time_series_df = get_time_series_df(tof_data, mass_axis, masses, names=cols, mass_range=True, timestamps=timestamps, metadata=metadata)
    
    time_series_df = time_series_df.sort_index()

    return time_series_df


def group_time_series_df(time_series_df, **kwargs):
    """
    Based on the groups listed in the config/voc-db.yml file,
    sum the time series dataframe to have those groups as columns.

    Inputs
    ------
    :param time_series_df: dataframe of the integrated counts/concentration for the specified m/Q values
    :type time_series_df: pd.Dataframe
    :param peak_list: path to configuration yml file
    :type peak_list: str

    Optional Arguments
    ------------------
    :param lookup_table: path to SMILES / functional groups lookup table
    :type lookup_table: str
    :param columns: the column names can either be SMILES strings ('smiles') or molecular formulas ('mf') 
                    of different compounds. default = 'smiles'

    Output
    ------
    :return: dataframe of the integrated counts/concentration for the specified functional groups
    :rtype: pd.Dataframe
    """
    #path to lookup table
    lookup_table = kwargs.pop('lookup_table', 'db/database.feather')
    #method -- either use smiles or mf to do the integration
    columns = kwargs.pop('columns', 'smiles')
    if columns in ['mf', 'smiles']:
        pass
    else: 
        raise Exception("Only `mf` and `smiles` are accepted inputs for columns")

    #load functional group lookup table
    fx_df = pd.read_feather(lookup_table)
    group_list = list(fx_df.columns)
    group_list.remove('mf')
    group_list.remove('smiles')

    #isolate only the columns which are in time_series_df
    if columns == 'mf':
        mf = time_series_df.columns.to_numpy()
        subset_df = fx_df.loc[fx_df[columns].isin(mf)]
    else:
        smiles = time_series_df.columns.to_numpy()
        subset_df = fx_df.loc[fx_df[columns].isin(smiles)]

    #get all of the compounds in each group
    groups_smiles_dict = {} 
    for g in group_list:
        subset_g = subset_df.loc[subset_df[g] == 1][columns].to_list()
        groups_smiles_dict[g] = {columns: list(set(subset_g)),}

    #build grouped dataframe
    grouped_df = pd.DataFrame()
    grouped_df.index = time_series_df.index
    # grouped_df['metadata'] = time_series_df['metadata']

    for group in groups_smiles_dict.keys():
        grouped_df[group] = time_series_df[groups_smiles_dict[group][columns]].sum(axis=1)

    return grouped_df
