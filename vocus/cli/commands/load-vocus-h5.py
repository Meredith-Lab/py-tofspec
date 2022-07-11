#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import h5py
from datetime import datetime, timedelta
import click

from ...exceptions import InvalidFileExtension, InvalidArgument

## methods for wrangling hdf5 file data and compiling into some properties
def load_data(file):
    """
    extracts useful data from Vocus hdf5 file.
    :param data: hdf5 filepath
    :type data: str
    """
    with h5py.File(file, "r") as f:
        timestamps = get_times(f)
        mass_axis = get_mass_axis(f)
        sum_spectrum = get_sum_spectrum(f)
        tof_data = get_tof_data(f, len(timestamps), len(mass_axis))
        metadata = get_metadata(f)

    return timestamps, mass_axis, sum_spectrum, tof_data, metadata

def get_times(f):
    """
    extracts array of timestamps that match up with ToF data from Vocus file
    """
    # get experiment start time from log file and transform string to datetime
    start_time = f['AcquisitionLog']['Log']['timestring'][0]
    start_time = datetime.strptime(start_time.decode('UTF-8'), "%Y-%m-%dT%H:%M:%S+00:00")

    # times of observation are recorded as second offsets from start time
    buftimes = np.array(f['TimingData']['BufTimes'])
    
    timestamps = np.array([start_time + timedelta(seconds=i) for i in buftimes.reshape(-1)])
    
    # when the Vocus stops recording measurements, it still finishes out its last five second interval,
    # and records the time of the empty measurements as the start time. This code sets the empty measurement
    # times to NaN
    mask = (timestamps == timestamps[0])
    mask[0] = False

    timestamps[mask] = np.nan

    return timestamps

def get_tof_data(f, t, n):
    """
    extracts array of ToF data of shape (t, n) where
    t = number of snapshots that were taken during the experiment, or in other words the number of 
    timesteps (typically seconds) that the experiment was running
    n = number of mass bins that the mass spec is equipped to observe
    """
    tof_data = np.array(f['FullSpectra']['TofData'])
    tof_data = tof_data.reshape(t, n)
    return tof_data

def get_metadata(f):
    """
    returns array of metadata that corresponds to each measurement. 
    The metadata is currently stored in:
    TPS2
    ---> TEMP_INLET target [C]
    by Jordan
    """
    # times of observation are recorded as second offsets from start time
    buftimes = np.array(f['TimingData']['BufTimes'])

    metadata = np.array(f['TPS2']['TwData'])
    try:
        metadata_array = np.array(metadata[:, 87])
        return np.repeat(metadata_array, buftimes.shape[1])
    except:
        metadata_array = metadata[:,:,85].reshape(-1)
        return metadata_array

def get_sum_spectrum(f):
    """
    returns array that is the sum of all the ToF data taken during the experiment
    """
    sum_spectrum = np.array(f['FullSpectra']['SumSpectrum'])
    return sum_spectrum

def get_mass_axis(f):
    """
    returns array of mass values that the ToF arrays correspond to
    """
    mass_axis = np.array(f['FullSpectra']['MassAxis'])
    return mass_axis