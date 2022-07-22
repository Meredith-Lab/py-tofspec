#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import rich_click as click

from ...utils import *
from ...exceptions import InvalidFileExtension, InvalidArgument

def config_command(file, output, **kwargs):
    #does file include a smiles column? -- defaults to False
    _smiles = kwargs.pop('smiles', False)

    #does file include an ion column? -- defaults to False and assumes that a mf column exists instead
    _ion = kwargs.pop('ion', False)

    #if user wants to specify a name or author
    name = kwargs.pop('name', None)
    author = kwargs.pop('author', None)

    #path to lookup table
    lookup_table = "tofspec/db/database.feather"

    # make sure the extension is either a csv or feather format
    file = Path(file)
    if file.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid input file extension")

    df = safe_load(file)
    df.columns = df.columns.str.lower()
    
    #check that input contains necessary mass range columns with correct names (case insensitive)
    if not pd.Series(['min', 'max']).isin(df.columns).all():
        raise InvalidArgument("FILE must contain columns: 'min', 'max' to describe the m/z integration range for each compound")
    #check that input contains either mf or smiles or both with correct names (case insensitive)
    if not pd.Series(['mf', 'ion', 'smiles']).isin(df.columns).any():
        raise InvalidArgument("FILE's columns must contain one of 'mf', 'smiles', 'ion' for functional grouping purposes")
    #check that the input contains a smiles column if the --smiles flag is passed

    if _smiles:
        if 'smiles' not in df.columns:
            raise InvalidArgument("If --smiles is passed, then FILE must contain a column named 'smiles'")
        # just parse the df and turn it into yaml
        data = df.to_dict('records')

        config_data = {'name':name,
                   'author': author,
                   'peak-list':data}
    else:
        #load functional group lookup table
        fx_df = pd.read_feather(lookup_table)
        if _ion:
            if 'ion' not in df.columns:
                raise InvalidArgument("If --ion is passed, then FILE must contain a column named 'ion'")
            df['mf'] = df['ion'].apply(deionize_regex)
        
        df = df.drop_duplicates(subset='mf', keep="last")

        # for now use the first SMILES found in the database depending on mf
        # we will also give the user an option to use all of the functional groups that correspond to a single isomer
        clean_df = df.merge(fx_df, how='inner', on='mf')[['mf','smiles', 'min', 'max']].drop_duplicates(subset='mf', keep="first").reset_index(drop=True)

        data = clean_df.to_dict('records')

        config_data = {'name':name,
                   'author': author,
                   'peak-list':data}
    
    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    write_yaml(output, config_data)