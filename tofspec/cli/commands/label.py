#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import rich_click as click

from tofspec.models import group_time_series_df

from ...models import *
from ...utils import safe_load
from ...exceptions import InvalidFileExtension, InvalidArgument

def label_command(file, output, **kwargs):
    tscol = kwargs.pop('tscol', None)
    ignore = kwargs.pop('ignore', None)
    columns = kwargs.pop('columns', 'smiles')

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid output file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    df = safe_load(file)

    label_df = group_time_series_df(df, lookup_table='tofspec/db/database.feather', columns=columns)

    if tscol is not None:
        label_df[tscol] = pd.to_datetime(df[tscol])
    if ignore is not None:
        label_df[ignore] = df[ignore]

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        label_df.to_csv(output)
    else:
        label_df.columns = label_df.columns.astype(str)
        label_df.reset_index().to_feather(output)