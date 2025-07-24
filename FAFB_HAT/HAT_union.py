# load HAT hemilineage CBF and union images

import os 
import pandas as pd
import nrrd
import argparse
import numpy as np
import sys

parser = argparse.ArgumentParser(description='combine a HAT CBF')

parser.add_argument('HAT_root_path', type=str, help='Path to the HAT root directory')

args = parser.parse_args()
# load HAT hemilineages names
HAT_table = pd.read_csv(os.path.join(args.HAT_root_path, 'hemilineage_summary.csv'))
HAT_union_image = None
for hemilineage in HAT_table['ito_lee_hemilineage'].values:
    # load CBF registered mesh
    HAT_file_path = os.path.join(args.HAT_root_path, f"{hemilineage}/{hemilineage}_CBF_registered_meshes.nrrd")
    if not os.path.exists(HAT_file_path):
        print(f"File not found: {HAT_file_path}")
        continue
    
    
    # read the files
    CBF_mesh, _ = nrrd.read(HAT_file_path)
    if HAT_union_image is None:
        HAT_union_image = CBF_mesh
    
    # save the combined mesh
    HAT_union_image = HAT_union_image + CBF_mesh

nrrd.write(os.path.join(args.HAT_root_path, f"combined_registered_meshes.nrrd"), HAT_union_image)