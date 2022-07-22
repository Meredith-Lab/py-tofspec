#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import rich_click as click

from ...exceptions import InvalidFileExtension
from ...utils import safe_load


def concat_command(files, output, **kwargs):

    # make sure the extension is csv
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    click.secho("Files to read: {}".format(files), fg='green')

    # read all files
    data = []
    with click.progressbar(files, label="Parsing files") as bar:
        for f in bar:
            tmp = safe_load(f)

            data.append(tmp)

    # concat all of the files together
    df = pd.concat(data, sort=False)

    #sorting based on timestamp column
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp', drop=True)
    df = df.sort_index()

    if df.empty:
        raise Exception("No data")

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)
