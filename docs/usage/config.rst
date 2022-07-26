:code:`config`
====================
.. raw:: html

    <embed>
        <hr>
    </embed>

The purpose of this command is to take a peak list in .csv format that the user provides and translate it
to the YAML format supported by this package.

PTR-TOF mass spectrometry generates data that might be interpreted in a variety of ways depending on the 
experiment set-up. The reagent that is used as the ionization source, as well as the calibration of the 
instrument, might both affect the exact *m/z* value at which a compound's signal is detected. For this 
reason, the user must provide a configuration file to guide the data processing. This config file is in a 
readable YAML format that looks like this:

.. code:: yaml

    name: example-peak-list
    author: Johnny Appleseed
    peak-list:
    -   mf: H2O
        smiles: O
        mass-range:
            min: 19.016
            max: 19.02
    -   mf: C2H2
        smiles: C#C
        mass-range:
            min: 27.021
            max: 27.025

There are 4 different inputs to describe each peak in the mass spectrum:

#. ``mf`` -- molecular formula
#. ``smiles`` -- SMILES (Simplified Molecular Input Line Entry System) string, provided for substructure matching purposes. (`learn more <https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html>`_)
#. ``mass-range / min`` -- *m/z* lower bound on peak integration
#. ``mass-range / max`` -- *m/z* upper bound on peak integration

Creating this configuration file is made easy by the `config <../api/cli.html#tofspec-config>`_ command. The
user must provide a .csv (or .feather) FILE in any of the 3 following formats:


.. csv-table:: 1. Ion Style (pass ``--ion`` flag)
   :file: ../../tests/datafiles/test_config_ion.csv
   :widths: 34, 33, 33
   :header-rows: 1

.. csv-table:: 2. Molecular Formula Style (don't pass a flag)
   :file: ../../tests/datafiles/test_config_mf.csv
   :widths: 34, 33, 33
   :header-rows: 1

.. csv-table:: 3. SMILES Style (pass ``--smiles`` flag)
   :file: ../../tests/datafiles/test_config_smiles.csv
   :widths: 25, 25, 25, 25
   :header-rows: 1

.. admonition:: Note on Molecular Identifiers

   To read about the thoughts that went into these three formats, and their key differences, see `more <../notes/isomers.html>`_.


Also ``name`` and ``author`` can be passed directly to the config command using the ``--name`` and ``--author`` options.

Below is an example command where **ion_peaks.csv**, a file in the format of #1 above, is transformed into a YAML peak
list saved to **my_peak_list.yml**.

.. code-block:: shell

   $ tofspec config -o my_peak_list.yml --ion ion_peaks.csv
