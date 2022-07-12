#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import click

from vocus.utils import safe_load

from ...models import Vocus
from ...exceptions import InvalidFileExtension, InvalidArgument

# Jordan wants functionality for integrating the timeseries data for each soil probe sampling run.
# In other words, we can use the metadata to sum the concentrations for each compound and soil column.

def metadata_integration_command(datapath, output, non_data=[100,10,98,99]):
    """
    datapath should be either a .csv or .feather file containing time series vocus data.
    Columns: timestamp, metadata, [compounds]
    """
    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid output file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    #load in time series dataframe -- output from timeseries or concat command
    df = safe_load(datapath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp', drop=True)

    #save list of data columns
    cols = list(df.columns)
    cols.remove('metadata')

    # assemble the dictionary for aggregating 
    # 1. sum the data columns
    # 2. take the mean time during sampling run
    # 3. keep same metadata
    col_dict = {i:np.sum for i in cols}
    agg_dict = {'timestamp':np.mean,
                'metadata': np.median,}
    agg_dict.update(col_dict)

    #group by metadata
    g = df.groupby(by='metadata')

    #filter non data values, we only care about probe measurements
    real_data = df.metadata.unique()
    real_data = list(set(real_data) - set(non_data))

    groups = []
    # for each probe
    for i in real_data:
        subgroup = g.get_group(i)
        #sort by time
        subgroup = subgroup.sort_index()
        #check for gaps -- integrate individual sampling runs
        subgroup[1] = subgroup.index.to_series().diff()
        subgroup[1] = subgroup[1] > timedelta(seconds=5) #more than 5 second break means new sampling scheme
        subgroup[1] = subgroup[1].cumsum()
        subgroup.reset_index(inplace=True)

        #do the integration -- sum over observations, take the mean time of the sampling run 
        subgroup = subgroup.groupby(1).agg(agg_dict)
        #reset index
        subgroup.set_index('timestamp', inplace=True)

        groups.append(subgroup)

    integrated_df = pd.concat(groups)

    integrated_df.sort_values('timestamp', inplace=True)

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        integrated_df.to_csv(output)
    else:
        integrated_df.reset_index().to_feather(output)