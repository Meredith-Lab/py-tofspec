#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import rich_click as click

from ...models import *
from ...utils import safe_load
from ...exceptions import InvalidFileExtension, InvalidArgument

def integrate_peaks_command(file, output, **kwargs):
    tscol = kwargs.pop('tscol', None)
    ignore = kwargs.pop('ignore', None)
    columns = kwargs.pop('columns', 'smiles')

    config = kwargs.pop('config', 'tofspec/config/peak-list.yml')
    peak_list = Path(config)
    if peak_list.suffix not in (".yml", ".yaml"):
        raise InvalidFileExtension("Invalid YAML file extension")

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid output file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    df = safe_load(file)

    timestamps = None
    metadata = None

    if tscol is not None:
        df[tscol] = pd.to_datetime(df[tscol])
        timestamps = df[tscol].to_numpy(dtype=np.datetime64)
        df.drop(tscol, axis=1, inplace=True)

    if ignore is not None:
        metadata = df[ignore].to_numpy()
        df.drop(ignore, axis=1, inplace=True)

    mass_axis = df.columns.to_numpy(dtype=np.float32)

    tof_data = df.to_numpy(dtype=np.float32)

    compound_df = time_series_df_from_yaml(tof_data, mass_axis, peak_list=config, columns=columns, timestamps=timestamps, metadata=metadata)

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        compound_df.to_csv(output)
    else:
        compound_df.columns = compound_df.columns.astype(str)
        compound_df.reset_index().to_feather(output)



