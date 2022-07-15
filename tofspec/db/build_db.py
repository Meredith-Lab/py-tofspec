from rdkit import Chem
from rdkit.Chem import PandasTools 
import pandas as pd
import yaml
import numpy as np

def read_yaml(name):
    with open(name) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

if __name__ == "main":
    df = pd.read_feather("database.feather")

    PandasTools.AddMoleculeColumnToFrame(df, smilesCol='smiles')

    #add all functional groups into the table
    substructures = read_yaml('substructures.yml')['substructures']

    for s in substructures:
        if s['name'] not in df.columns:
            # RDKit substructure matching
            df[s['name']] = df['ROMol'].map(lambda x: x.HasSubstructMatch(Chem.MolFromSmarts(s['smarts'])), na_action='ignore')
            # set to 1s and 0s rather than True / False
            df[s['name']] = df[s['name']].astype(int)
        else:
            pass
    
    # add BTEX column based on molecular formulas
    btex_formulas = ['C6H6', 'C7H8', 'C8H10']
    df['BTEX'] = np.where(df['mf'].isin(btex_formulas), 1, 0)

    #drop Mol column
    df = df.drop(['ROMol'], axis=1)

    #to feather
    df.to_feather("database.feather")