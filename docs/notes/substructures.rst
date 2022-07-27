Substructure Database
=======================================

To make the `label <../usage/label.html>`_ command possible, we created a database using data from 
`PubChem <https://pubchem.ncbi.nlm.nih.gov/classification/#hid=72>`_ and RDKit's 
`SMARTS <https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html>`_-based substructure matching
functionality. 

.. admonition:: Current Supported Functional Groups / Substructures
   :class: dropdown

   hydroxyl, carbonyl, carboxyl, amine, alcohol, ether, ketone, halide, ester, amide, aldehyde,
   aromatic, amino acid, nitrate, phenol, nitro, phosphoric acid, phosphoric ester, sulfate, sulfonate,
   thiol, carbothioester

Add another substructure to the database
-----------------------------------------

1. Clone our repo to your machine
2. Install RDKit
3. Navigate to the **tofspec/db** folder
4. Open the **substructures.yml** file
5. Add your substructure(s) and the corresponding SMARTS string to the list, and save changes
6. Run ``build_db.py``

It might take a few minutes, but **database.feather** will be updated with your substructure(s) of choice!