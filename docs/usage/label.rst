:code:`label`
=======================

.. raw:: html

    <embed>
        <hr>
    </embed>

The purpose of this command is to take a .csv (or .feather) of compound time series data and output an 
integrated time series of functional groups.

From the format discussed on the `integrate-peaks <integrate-peaks.html>`_ guide, to a table that looks like this:

.. list-table:: Labeled Time Series
   :widths: 25 25 25 25
   :header-rows: 1
   :stub-columns: 0

   * -
     - func group 1
     - func group 2
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

The `label <../api/cli.html#tofspec-label>`_ command takes the same optional arguments as 
`integrate-peaks <integrate-peaks.html>`_ to describe your input and customize your output. Pass ``-ts, --tscol`` 
with the name of your timestamp column if there is one in your input file. Pass ``-i, --ignore`` with the
names of any metadata columns that you want to be passed from input to output. Choose whether you want to
sum functional groups by molecular formula (``-col=mf``) or SMILES (``-col=smiles``). If molecular formula
is chosen, then functional groups corresponding to all of the isomers within our 
`database <../notes/substructures.html>`_ will be used. If SMILES is chosen, then only the specific
functional groups for the single isomer denoted by the SMILES string are used. As always, specify your
output path with ``-o, --output``.

.. raw:: html

    <embed>
        <hr>
    </embed>

Below is an example command where `integrated_data.csv`, is labeled / integrated by functional group
and saved to `labeled_data.csv`.  

`integrated_data.csv` has a timestamp column named 'Time', and columns denoted by molecular formula.

.. code-block:: shell

   $ tofspec label -o labeled_data.csv -ts Time -col=mf integrated_data.csv