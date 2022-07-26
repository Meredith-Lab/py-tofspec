:code:`load`
====================
.. raw:: html

    <embed>
        <hr>
    </embed>

The purpose of this command is to take a raw mass spectrometry data file that the user provides and 
translate it to the .csv or .feather format supported by this package:

.. list-table:: PTR-TOF-MS matrix
   :widths: 25 25 25 25
   :header-rows: 1
   :stub-columns: 0

   * -
     - m/z bin 1
     - m/z bin 2
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

The `load <../api/cli.html#tofspec-load>`_ command takes the ``-i, --instrument`` and ``-f, format`` arguments and
parses the raw data file accordingly. At the moment, the only supported instrument is the "`Vocus <https://www.tofwerk.com/products/vocus/>`_" PTR-TOF-MS 
produced by TOFWERK. If you have raw data from a different mass spec that you would like to plug into our tool,
we encourage you to write a loader and submit a pull request according to the guidelines laid out on the 
`Contribution <../contributing/contributing.html>`_ page.

Below is an example command where the raw data from `V1_20XX-XX-XX.h5`, a Vocus file, is parsed into a 
.csv format and saved to `raw_data.csv`.

.. code-block:: shell

   $ tofspec load -o raw_data.csv -i vocus -f h5 V1_20XX-XX-XX.h5
