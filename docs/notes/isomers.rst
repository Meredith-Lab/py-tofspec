Compound Identifiers and Isomers
=======================================

Here we outline the three different compound identifiers that are used and their distinctions.
We also describe certain methods used in the `config <../usage/config.html>`_ command.

1. Ion Formulas
-----------------

`Mass spectrometry <https://www.broadinstitute.org/technology-areas/what-mass-spectrometry#:~:text=Mass%20spectrometry%20is%20an%20analytical,the%20sample%20components%20as%20well.>`_
begins with the ionization of molecules within a sample before they are passed to the detector. Hence, what
is being detected is actually an ion. So, many peak lists might rightfully give their peak identifiers as
ion formulas. 

This is why we accept ion formula peak lists as inputs to the `config <../usage/config.html>`_ command.
We translate the ion formulas to molecular formulas by subtracting an H using regular expressions, and then search
our database for the most common isomer of that molecular formula.

2. Molecular Formulas
----------------------

While ions are what is detected by a mass spectometer, neutral molecules are usually what is present in the
sample. We made the decision to use molecular formulas, not ions, as our primary identifier in our database
used to do substructure matching. 

If only a molecular formula is given in the input to the 
`config <../usage/config.html>`_ command, then we search our database for the most common isomer of that 
molecular formula.

3. SMILES
-----------------

SMILES are identifiers that describe the `structure` of a chemical species. This makes them more
specific than either of the above identifiers, as a single formula might have many different isomers
with unique structures (and therefore unique substructures!). 

The most foolproof way to create a peak list configuration file is by providing a column with SMILES strings
for each peak / compound. This way there is no ambiguity in the database search. 