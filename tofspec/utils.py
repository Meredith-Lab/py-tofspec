#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import yaml
from pathlib import Path

from .exceptions import InvalidFileExtension

def safe_load(fpath, **kwargs):
    """Load and return a file
    """
    p = Path(fpath)

    if p.suffix == ".csv":
        as_csv = True
    elif p.suffix == ".feather":
        as_csv = False
    else:
        raise InvalidFileExtension

    sample = pd.read_csv(fpath, nrows=1) if as_csv else pd.read_feather(fpath)
    dtypes = sample.dtypes # Get the dtypes
    cols = sample.columns # Get the columns

    dtype_dictionary = {} 
    for c in cols:
        if str(dtypes[c]) == 'float64':
            dtype_dictionary[c] = 'float32'
        else:
            dtype_dictionary[c] = str(dtypes[c])

    tmp = pd.read_csv(fpath, dtype=dtype_dictionary) if as_csv else pd.read_feather(fpath)
    

    # drop the extra column if it was added
    if "Unnamed: 0" in tmp.columns:
        del tmp["Unnamed: 0"]

    return tmp


## reading YAML config files

def write_yaml(name, data):
    with open(name, 'w') as f:
        documents = yaml.dump(data, f, indent=4, default_flow_style=False, sort_keys=False)

def read_yaml(name):
    with open(name) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def build_peak_list(mf, smiles, min, max, **kwargs):
    name = kwargs.pop('name', None)
    author = kwargs.pop('author', None)

    data = {'name':name,
            'author': author,
            'peak-list':[{
                'mf': mf[i],
                'smiles': smiles[i],
                'mass-range':{
                    'min':min[i],
                    'max':max[i],
                }}for i in range(len(smiles))
                ]}
    
    return data

def peak_list_from_dict(data):
    mf = []
    smiles = []
    min = []
    max = []
    for i in data['peak-list']:
        mf.append(i['mf'])
        smiles.append(i['smiles'])
        min.append(i['mass-range']['min'])
        max.append(i['mass-range']['max'])
    return mf, smiles, min, max