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

    tmp = pd.read_csv(fpath, nrows=1, header=None) if as_csv else pd.read_feather(fpath)

    if tmp.iloc[0, 0] == "deviceModel": # hack to deal with PID data format
        tmp = pd.read_csv(fpath, skiprows=3) if as_csv else pd.read_feather(fpath, skiprows=3)
    else:
        tmp = pd.read_csv(fpath) if as_csv else pd.read_feather(fpath)

    # drop the extra column if it was added
    if "Unnamed: 0" in tmp.columns:
        del tmp["Unnamed: 0"]

    return tmp


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