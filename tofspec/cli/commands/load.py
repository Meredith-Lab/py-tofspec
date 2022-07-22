#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import h5py
import rich_click as click

from ...exceptions import InvalidFileExtension, InvalidArgument
from ...load import *

def load_command(file, output, **kwargs):
    instrument = kwargs.pop('instrument', 'vocus')
    file_format = kwargs.pop('format', 'h5')
    metadata_ = kwargs.pop('metadata', False)
    
    # right now we can only read Vocus files
    if instrument != 'vocus' or file_format != 'h5':
        raise InvalidArgument("There is currently only loading support for .h5 files from the TOFWERK PTR-TOF-MS Vocus instrument")

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid output file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    #load Vocus data
    if metadata_:
        timestamps, mass_axis, tof_data, metadata = load_vocus_data(file, metadata=metadata_)
        #assemble dataframe format
        df = pd.DataFrame(tof_data, columns=mass_axis)
        df['timestamp'] = timestamps
        df['metadata'] = metadata
    else:
        timestamps, mass_axis, tof_data = load_vocus_data(file, metadata=metadata_)
        #assemble dataframe format
        df = pd.DataFrame(tof_data, index=pd.DatetimeIndex(timestamps), columns=mass_axis)
        df['timestamp'] = timestamps

    # save the file
    click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.columns = df.columns.astype(str)
        df.reset_index().to_feather(output)

    
    