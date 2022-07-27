:code:`concat`
=======================

.. raw:: html

    <embed>
        <hr>
    </embed>

The purpose of the `concat <../api/cli.html#tofspec-concat>`_ command is to take a bunch of files of the same type (either .csv or feather) 
and concatenate them together. To use, you must provide either a list of files or a wildcard argument 
that will glob all of the files together. FILES is the only required argument.

.. raw:: html

    <embed>
        <hr>
    </embed>

Below is an example of a wildcard argument that will grab all files in the directory that begin with 
**data** and are **.csv**'s. The concatenated output is saved to **path/output.csv**.

.. code-block:: shell

   $ tofspec concat -o path/output.csv path/data*.csv

You could also explicitly define the individual files to concatenate:

.. code-block:: shell

   $ tofspec concat path/file-1.csv path/file-2.csv