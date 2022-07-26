:code:`integrate-peaks`
=======================
.. raw:: html

    <embed>
        <hr>
    </embed>

The purpose of this command is to take a .csv (or .feather) of raw mass spectrometry data, and a peak list
in the accepted YAML format, and output an integrated time series of compounds.

From the raw format discussed on the `load <load.html>`_ guide, to a table that looks like this:

.. list-table:: Compound Time Series
   :widths: 25 25 25 25
   :header-rows: 1
   :stub-columns: 0

   * -
     - mf or smiles
     - mf or smiles
     - ...
   * - timestamp 1
     - #
     - #
     - #
   * - timestamp 2
     - #
     - #
     - #
   * - ...
     - #
     - #
     - #

The `integrate-peaks <../api/cli.html#tofspec-integrate-peaks>`_ command requires that the user specifies
a peak list with the ``-c, --config`` argument. Beyond that, their are some optional arguments to describe
your input and customize your output. Pass ``-ts, --tscol`` with the name of your timestamp column if there
is one in your input file. Pass ``-i, --ignore`` with the names of any metadata columns that you want to be
passed from input to output. And choose whether you want your compound columns to be denoted by molecular 
formula (``-col=mf``) or SMILES (``-col=smiles``). As always, specify your output path with ``-o, --output``.

.. raw:: html

    <embed>
        <hr>
    </embed>

Below is an example command where `raw_data.csv`, is integrated based on the peaks specified in
`my_peak_list.yml` and saved to `integrated_data.csv`.  

`raw_data.csv` has a timestamp column named 'Time', and `integrated_data.csv` will have columns
denoted by molecular formula.

.. code-block:: shell

   $ tofspec integrate-peaks -o integrated_data.csv -ts Time -c my_peak_list.yml -col=mf raw_data.csv

.. important::

   The purpose of the ``-col`` argument is not just stylistic. It plays a role in the ultimate `label <label.html>`_-ing 
   of data which is discussed in the next command.