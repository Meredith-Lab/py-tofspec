# vocus
`vocus` is a python package and command line tool for wrangling Vocus PTR-TOF-MS data, and generating labeled time-series datasets that are useful for analyzing data, visualizing data, building machine learning models, and more.

Comprehensive documentation for the package is under construction.
The docs below should provide an overview of the command-line capabilities. When in doubt, run `vocus -h`.

# Docs

## Generate Vocus Time Series from `.h5` files

The Vocus spits out huge `.h5` files at user-input intervals that are in TOF bin format. The `timeseries` command will parse the `.h5` files and extract the meaningful data. Then, a YAML configuration file filled with peak data is used to integrate the TOF data and generate a time series dataframe for the inculded compounds. The YAML file should be in the following format:

```YAML
name: nsf-sits
author: QuantAQ, Inc.
compounds:
-   compound: isoprene
    ion: C5H9+
    mf: C5H8
    mass-range:
        min: 69.065
        max: 69.075
        center: 69.0698776245
- ...
...
```

The `timeseries` command takes the `.h5` files within DATAPATH, reads the input YAML file or uses the default (`vocus/config/mass_list.yml`) and saves the OUTPUT to a specified path (default `output.csv`)

```sh
$ vocus timeseries [OPTIONS] DATAPATH
```
Options:
- -o, --output <output>
    - output filepath (must be .csv or .feather)
- -y, --yaml
    - YAML file compound list used to build the time series
- -c, --columns
    - column names in output dataframe (compound, mf, ion)


## Integrate Time Series Data based on Metadata Column

For the NSF-SiTS experiment, the Vocus is continuously analyzing samples from a rotation of soil probes, which each have a unique identifier saved in the metadata column of the time-series dataframe generated with the above command.

The `metadata_integrate` command takes a time-series DATAPATH, integrates for each sampling run, and saves the OUTPUT to a specified path (default `output.csv`)

```sh
$ vocus metadata_integrate [OPTIONS] DATAPATH
```
Options:
-  -o, --output TEXT 
    - output filepath (must be .csv or .feather)


## Concatenate Time Series Data

If the user wanted to concatenate multiple time-series files, they would use the `concat` command.

Concatenate FILES together and save to OUTPUT. FILES is the collection or
list of files that you are concatenating together. They can be provided as
a list, each separated by a space, or by using a wildcard and providing the path with wildcard.

```sh
$ vocus concat [OPTIONS] [FILES]...
```
Options:
-  -o, --output TEXT 
    - The filepath where you would like to save the file

## Merge Time Series Data

If the user wanted to merge Vocus time-series data with another instrument's data, they would use the `merge` command.

Merge time series .csv (or .feather) files along their timestamp axis
```sh
$ vocus merge [OPTIONS] [FILES]...
```
Options:
-  -o, --output TEXT 
    - The filepath where you would like to save the file
