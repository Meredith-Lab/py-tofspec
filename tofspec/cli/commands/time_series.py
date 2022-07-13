#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import click

from ...models import Vocus
from ...exceptions import InvalidFileExtension, InvalidArgument

def time_series_command(datapath, output, **kwargs):
    path_to_mass_list = kwargs.pop('path_to_mass_list', 'vocus/config/mass_list.yml')
    path_to_mass_list = Path(path_to_mass_list)
    if path_to_mass_list.suffix not in (".yml", ".yaml"):
        raise InvalidFileExtension("Invalid YAML file extension")

    columns = kwargs.pop('columns', 'mf')

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid output file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    datapath = Path(datapath)
    #if path is single .h5 file
    if datapath.suffix == ".h5":
        v = Vocus(datapath)
    #if path is folder containing .h5 files 
    else:
        datalist = list(datapath.glob("*.h5"))
        if not datalist:
            raise InvalidArgument("No .h5 files in your directory")
        else:
            v = Vocus(list(datapath.glob("*.h5")))

    click.secho('Loaded files!', fg='green')

    v.time_series_df_from_yaml(columns=columns, path_to_mass_list=path_to_mass_list)

    click.secho('Built time series!', fg='green')

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        v.time_series_df.to_csv(output)
    else:
        v.time_series_df.reset_index().to_feather(output)
    
    