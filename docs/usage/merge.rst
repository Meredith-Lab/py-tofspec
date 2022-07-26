:code:`merge`
=======================

.. raw:: html

    <embed>
        <hr>
    </embed>

There may be a need to `merge <../api/cli.html#tofspec-merge>`_ two (or more) files on their timestamp. For example, if you are running
a different instrument alongside your mass spectrometer and would like to merge the data into a 
single file for easier analysis. The only required argument is the file(s) to merge together. Additionally,
you can override the name of the timestamp column (``-ts, --tscol``) as well as define the output file 
destination (``-o, --output``).

To merge together two files with the timestamp column 'Time' and define your own output destination:

.. code-block:: shell

    $ tofspec merge -o dest-path/final-file.csv -ts Time path/file-1.csv path/file-2.csv