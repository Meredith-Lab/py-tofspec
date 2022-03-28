import click
import pkg_resources

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

__version__ = pkg_resources.get_distribution('vocus').version

#set up cli tool
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
@click.pass_context
def main(ctx):
    pass

#add concat command
@click.command("concat", short_help="concatenate files together")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
def concat(files, output, **kwargs):
    """Concatenate FILES together and save to OUTPUT.
    FILES is the collection or list of files that you are concatenating together. They 
    can be provided as a list or by using a wildcard and providing the path with wildcard.
    """
    from .commands.concat import concat_command

    concat_command(files, output, **kwargs)

#add timeseries command
@click.command("timeseries", short_help="build a time series from vocus files")
@click.argument("datapath", nargs=1, type=click.Path())
@click.option("-y", "--yaml", default="vocus/config/mass_list.yml", help="YAML file compound list used to build the time series", type=click.Path())
@click.option("-o", "--output", default="output.csv", help="output filepath (must be .csv or .feather)", type=str)
@click.option("-c", "--columns", default="mf", help="column names in output dataframe (compound, mf, ion)", type=str)
def timeseries(datapath, yaml, output, columns, **kwargs):
    """Load and compute timeseries for Vocus .h5 file(s)
    """
    from .commands.time_series import time_series_command

    time_series_command(datapath, output, columns=columns, path_to_mass_list=yaml, **kwargs)

#add metadata integration command
@click.command("metadata_integrate", short_help="integrate time series data for each sampling run")
@click.argument("datapath", nargs=1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="output filepath (must be .csv or .feather)", type=str)
def metadata_integrate(datapath, output, **kwargs):
    """Use the metadata to integrate/downsample time series data for each sampling run
    """
    from .commands.metadata_integration import metadata_integration_command

    metadata_integration_command(datapath, output)  

#add merge integration command
@click.command("merge", short_help="merge time series data")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="output filepath (must be .csv or .feather)", type=str)
def merge(files, output, **kwargs):
    """Merge time series .csv files along their timestamp axis
    """
    from .commands.merge import merge_command

    merge_command(files, output)  


#add all commands
main.add_command(concat)
main.add_command(timeseries)
main.add_command(metadata_integrate)
main.add_command(merge)
