import rich_click as click
import pkg_resources

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

__version__ = pkg_resources.get_distribution('py-tofspec').version

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

@click.command("merge", short_help="merge two files together on their timestamp")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-ts", "--tscol", default="timestamp", help="The column by which to join the files", type=str)
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def merge(files, tscol, output, verbose, **kwargs):
    """Merge FILES together and save to OUTPUT.
    """
    from .commands.merge import merge_command

    merge_command(files, output, tscol=tscol, verbose=verbose, **kwargs)

#add config command
@click.command("config", short_help="build peak list from .csv")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-s", "--smiles", is_flag=True, default=False, help="Does FILE have a smiles column?")
@click.option("-ion", "--ion", is_flag=True, default=False, help="Does FILE have an ion column instead of a mf column?")
@click.option("-n", "--name", default=None, help="Name for the peak list", type=str)
@click.option("-a", "--author", default=None, help="Author of the peak list", type=str)
@click.option("-o", "--output", default="output.yaml", help="The filepath where you would like to save the peak list", type=str)
def config(file, output, **kwargs):
    """Use FILE to construct a peak list configuration .yaml file that will be used to integrate peaks
    and label / group data.
    """
    from .commands.config import config_command

    config_command(file, output, **kwargs)


#add load command
@click.command("load", short_help="parse raw mass spec data files")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-i", "--instrument", default="vocus", help="The instrument that FILE comes from", type=str)
@click.option("-f", "--format", default="h5", help="The format/file extension of FILE", type=str)
@click.option("-m", "--metadata", is_flag=True, default=False, help="Does the file include metadata?")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
def load(file, output, **kwargs):
    """Parse mass spec FILE and save relevant data to OUTPUT.
    Read TOF data matrix from FILE. The structure of FILE is determined by the 
    optional --instrument and --format arguments. Currently, only 'vocus' and 'h5' are accepted.
    """
    from .commands.load import load_command

    load_command(file, output, **kwargs)

#add integrate peaks command
@click.command("integrate-peaks", short_help="integrate ion peaks in raw mass spec data")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-c", "--config", default="tofspec/config/peak-list.yml", help="The peak list .yml file that guides the integration process", type=click.Path())
@click.option("-ts", "--tscol", help="Column in FILE which contains timestamps")
@click.option("-i", "--ignore", help="Names of metadata column(s) which should be ignored in the integration and passed to OUTPUT untouched")
@click.option("-col", "--columns", type=click.Choice(['smiles', 'mf'], case_sensitive=False),  default='smiles', help="Choose either molecular formula (`mf`) or SMILES string (`smiles`) as the column names of OUTPUT")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
def integrate_peaks(file, output, **kwargs):
    """Convert FILE, a matrix of raw PTR-TOF-MS data (TOF bins X timestamps) to a time series of
         integrated ion counts/concentrations for ions specified in the peak list (CONFIG).
    """
    from .commands.integrate_peaks import integrate_peaks_command

    integrate_peaks_command(file, output, **kwargs)

@click.command("label", short_help="sum compounds counts/concentrations by substructure")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-ts", "--tscol", help="column in FILE which contains timestamps")
@click.option("-i", "--ignore", help="names of metadata column(s) which should not be included in the integration but should be passed to OUTPUT")
@click.option("-col", "--columns", type=click.Choice(['smiles', 'mf'], case_sensitive=False),  default='smiles', help="choose either molecular formula (`mf`) or SMILES string (`smiles`) as the column names of FILE")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
def label(file, output, **kwargs):
    """Convert FILE, a matrix of compound counts/concentrations, to a time series of integrated
        substructure/functional group concentrations. For more info on how to choose different substructures...
    """
    from .commands.label import label_command

    label_command(file, output, **kwargs)


#add all commands
main.add_command(concat)
main.add_command(merge)
main.add_command(config)
main.add_command(load)
main.add_command(integrate_peaks)
main.add_command(label)
