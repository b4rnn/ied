################
### API FOR TRAINING NANOMODELS
#@{PIXEL ASSASSIN}
import pandas as pd
import sys
import os
import re
import hnswlib
import argparse 
import numpy as np

def data_prep(bin_path):
    #df = pd.DataFrame(list_val)
    df = pd.read_json(bin_path, lines=True)
    df['facial_weights'] = df.apply(lambda df: df['facial_weights'], axis=1)
    return df

def main(args):
    #df = pd.read_json (args.bin_path, lines=True)
    df = data_prep(args.bin_path)
    covix = []
    len_covix =len(df['facial_weights'].values.tolist())
    covix_nested_list =df['facial_weights'].values.tolist()
    #set hwlib params
    dim = 512
    num_elements = len_covix
    # Declaring index
    p = hnswlib.Index(space = 'l2', dim = dim) # possible options are l2, cosine or ip
    # Initing index - the maximum number of elements should be known beforehand
    p.init_index(max_elements = num_elements, ef_construction = 600, M = 512)
    #get all indices
    data_labels = np.arange(num_elements)
    # Element insertion (can be called several times):
    p.add_items(covix_nested_list, data_labels)
    # Controlling the recall by setting ef:
    p.set_ef(60) # ef should always be > k
    #models saved inside distinct virtual environment
    p.save_index(str(args.pod_path) + str(num_elements) +'_' + str(args.bin_index) + '.bin')
    print("created "+ str(num_elements) +'_' + str(args.bin_index) + ".bin")

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--bin_path', type=str, help='Json bin path')
    parser.add_argument('--bin_index', type=str, help='Json bin number')
    parser.add_argument('--pod_path', type=str, help='Json bin virtualized path')
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
