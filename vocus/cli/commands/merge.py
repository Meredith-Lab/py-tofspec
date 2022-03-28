#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import click

from ...exceptions import InvalidFileExtension
from ...utils import safe_load

def merge_command(files, output, **kwargs):
    # create an array of timestamp column names to try
    tscols = ["timestamp_iso", "timestamp"]
    tscol = "timestamp_iso"
    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    click.secho("Files to read: {}".format(files), fg='green')

    df = pd.DataFrame()
    with click.progressbar(files, label="Parsing files") as bar:
        for f in bar:
            tmp = safe_load(f)
            print(tmp.head(2))
            
            # check for the column name and set to best guess
            for c in tscols:
                if c in tmp.columns:
                    tscol = c
                    break
                
            if not tscol in tmp.columns:
                click.secho("Time tscol was not found in {}; skipping file.".format(f), fg='red')
                continue
                
            # convert the timestamp column to a pandas datetime
            if not pd.core.dtypes.common.is_datetime_or_timedelta_dtype(tmp[tscol]):
                tmp[tscol] = tmp[tscol].apply(lambda x: pd.to_datetime(x, errors='coerce'))
            
            # drop the bad rows
            tmp = tmp.dropna(how='any', subset=[tscol])

            # re-convert to timestamp in case it's not
            if not pd.core.dtypes.common.is_datetime_or_timedelta_dtype(tmp[tscol]):
                tmp[tscol] = tmp[tscol].apply(lambda x: pd.to_datetime(x, errors='raise'))
            
            # localize the timezone if needed
            tmp[tscol] = tmp[tscol].apply(lambda x: x.tz_localize("UTC") if not x.tzinfo else x)

            # set the index
            tmp.set_index(tscol, inplace=True)

            # merge with the other files
            df = pd.merge(df, tmp, left_index=True, right_index=True, how='outer') 

            df.index.rename('timestamp', inplace=True)      

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)