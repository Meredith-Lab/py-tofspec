#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import yaml

#For normalization of y-axis
def normalize_data(data):
    '''
    Normalizes data to be in the range of 0 to 1. 
    
    Inputs:
    :param data: list of 1 dimensional data to be normalized
    :type: array-like
    Outputs:
    :return normalized: normalized data
    :rtype: array-like
    '''
    normalized = (data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data))
    return normalized

def df_from_arrays(arrays, names):
    """
    Turn a list of arrays and a list of names into a pandas dataframe where the 
    names are column names and the arrays are data
    """
    data_dict = dict(zip(names, arrays))
    df = pd.DataFrame(data_dict)
    return df


def resample(data, resample_len):
        """
        Resample on the timeseries.
        :param resample_len: The resample period using normal 
            Pandas conventions.
        :type resample_len: string
        :return: A timeseries that has been resampled with 
            period `rs`.
        :rtype: an object from the same class as `self`
        """
        obj_cols = (
            data
            .select_dtypes(include=['object'])
            .resample(resample_len)
            .first()
        )
        num_cols = (
            data
            .select_dtypes(exclude=['object'])
            .resample(resample_len)
            .mean()
        )

        # re-merge the two dataframes
        merged = pd.merge(num_cols, obj_cols, left_index=True, 
                          right_index=True, how='outer')

        return merged
    
## reading YAML config files

def read_yaml(name):
    with open(name) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def mass_list_from_dict(data):
    compound = []
    ion = []
    mf = []
    min = []
    max = []
    center = []
    for i in data['compounds']:
        compound.append(i['compound'])
        ion.append(i['ion'])
        mf.append(i['mf'])
        min.append(i['mass-range']['min'])
        max.append(i['mass-range']['max'])
        center.append(i['mass-range']['center'])
    return compound, ion, mf, min, max, center

def voc_lists_from_dict(data):
    name = []
    formula = []
    smiles = []
    groups = []
    for i in data['compounds']:
        name.append(i['iupac-name'])
        formula.append(i['molecular-formula'])
        smiles.append(i['smiles'])
        groups.append(i['groups'])
    return name, formula, smiles, groups