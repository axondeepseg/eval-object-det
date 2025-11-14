'''
This script takes as input 3 things:
- a folder with semantic segmentations (output of a segmentation network)
- a folder with manual counts (in XML format)
- a 'subj_list.txt' file listing the subjects to process

Author: Armand Collin
'''

from pathlib import Path
from AxonDeepSeg.morphometrics import launch_morphometrics_computation
from AxonDeepSeg.visualization.merge_masks import merge_masks
import argparse
import pandas as pd

# this pixel resolution is specific to the project with APP-cKO mice
PX_SIZE = 0.005648  # in microns (5.648 nm)


def load_myelinated_morpho(fname, verbose=False):
    df = pd.read_excel(fname)
    n_filtered = 0

    #TODO: eventually we will want to make these ad hoc rules customizable 
    # exclude axons with diam < 0.1
    outliers = df[df['axon_diam (um)'] < 0.1]
    if verbose:
        print(f'removing {len(outliers)} lines with axon_diam < 0.1 um')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)

    # check for NaNs
    outliers = df[df['gratio'].isna()]
    if verbose:
        print(f'removing {len(outliers)} lines with NaN gratio')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)

    # check invalid g ratios
    outliers = df[df['gratio'] >= 1]
    if verbose:
        print(f'removing {len(outliers)} lines with gratio >= 1')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)
    outliers = df[df['gratio'] <= 0]
    if verbose:
        print(f'removing {len(outliers)} lines with gratio <= 0')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)

    if verbose:
        print(f'Removed a total of {n_filtered} myelinated axons according to post hoc screening rules.')

    return df, n_filtered

def load_unmyelinated_morpho(fname, verbose=False):
    df = pd.read_excel(fname)
    n_filtered = 0

    # threshold for diameter is 0.05 um
    outliers = df[df['axon_diam (um)'] < 0.05]
    if verbose:
        print(f'removing {len(outliers)} lines with axon_diam < 0.05 um')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)

    # check for minimal solidity - under 0.8, the shape is extremely concave
    outliers = df[df['solidity'] < 0.8]
    if verbose:
        print(f'removing {len(outliers)} lines with solidity < 0.8')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)

    # limit max axon area
    outliers = df[df['axon_area (um^2)'] > 1]
    if verbose:
        print(f'Removing {len(outliers)} lines with axon_area > 1 um^2')
    n_filtered += len(outliers)
    df = df.drop(outliers.index)

    if verbose:
        print(f'Removed a total of {n_filtered} unmyelinated axons according to post hoc screening rules.')

    return df, n_filtered

def main():
    parser = argparse.ArgumentParser(description="Compute morphometrics from semantic segmentations and filter them based on size.")
    parser.add_argument('--seg_dir', type=str, required=True, help='Path to the folder containing semantic segmentations.')
    parser.add_argument('--counts_dir', type=str, required=True, help='Path to the folder containing manual counts in XML format.')
    #TODO: add support for Brad's CSV format
    parser.add_argument('--subj_list', type=str, required=True, help='Path to the subj_list.txt file.')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to the output folder where results will be saved.')
    
    args = parser.parse_args()
    
    seg_dir = Path(args.seg_dir)
    counts_dir = Path(args.counts_dir)
    subj_list_path = Path(args.subj_list)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(subj_list_path, 'r') as f:
        subjects = [line.strip() for line in f.readlines()]
    nb_subjects = len(list(seg_dir.glob('*_seg-myelin*')))
    
    # if no axonmyelin mask is found, create them
    has_axonmyelin_masks = len(list(seg_dir.glob('*_seg-axonmyelin*'))) > 0
    if not has_axonmyelin_masks:
        print('I did not find any combined axonmyelin mask. Creating them for you.') 
        for axon_mask_path in seg_dir.glob('*_seg-axon.png'):
            myelin_mask_path = str(axon_mask_path).replace('-axon', '-myelin')
            merge_masks(axon_mask_path, myelin_mask_path)

    # ------------------------------------------------- #
    #     compute morphometrics (myelinated axons)      #
    # ------------------------------------------------- #
    nb_morpho_files = len(list(seg_dir.glob('*_axon_morphometrics.xlsx')))
    if nb_morpho_files == nb_subjects:
        print('Found as many morphometric files as nb of subjects. Skipping (myelinated) morphometric computation step.')
    else:
        argv = [
            '-i', str(seg_dir),
            '-s', str(PX_SIZE),
            '-c', 
        ]
        try:
            print('Computing morphometrics for MYELINATED axons.')
            launch_morphometrics_computation.main(argv)
        except SystemExit as e:
            if e.code != 0:
                print('ERROR during morphometric computation for myelinated axons')

    # ------------------------------------------------- #
    #     compute morphometrics (unmyelinated axons)    #
    # ------------------------------------------------- #
    nb_umorpho_files = len(list(seg_dir.glob('*_uaxon_morphometrics.xlsx')))
    if nb_umorpho_files == nb_subjects:
        print('Found as many morphometric files as nb of subjects. Skipping (unmyelinated) morphometric computation step.')
    else:
        argv = [
            '-i', str(seg_dir),
            '-s', str(PX_SIZE),
            '-u',
        ]
        try:
            print('Computing morphometrics for UNMYELINATED axons.')
            launch_morphometrics_computation.main(argv)
        except SystemExit as e:
            if e.code != 0:
                print('ERROR during morphometric computation for unmyelinated axons')

    # ------------------------------------------------- #
    #               filter morphometrics                #
    # ------------------------------------------------- #
    m_morpho_paths = seg_dir.glob('*_axon_morphometrics.xlsx')
    u_morpho_paths = seg_dir.glob('*_uaxon_morphometrics.xlsx')

    lines_removed = {}
    for m_morpho_p, u_morpho_p in zip(m_morpho_paths, u_morpho_paths):
        m_df, m_nb_filtered = load_myelinated_morpho(str(m_morpho_p))
        m_new_fname = m_morpho_p.name.replace('.xlsx', '_filtered.xlsx')
        m_df.to_excel(output_dir / m_new_fname)

        u_df, u_nb_filtered = load_unmyelinated_morpho(str(u_morpho_p))
        u_new_fname = u_morpho_p.name.replace('.xlsx', '_filtered.xlsx')
        u_df.to_excel(output_dir / u_new_fname)

        # logging the nb of filtered lines to monitor improvement
        base_name = str(m_morpho_p).replace('_axon_morphometrics.xlsx', '')
        lines_removed[base_name] = {
            'm_lines_removed': m_nb_filtered,
            'u_lines_removed': u_nb_filtered
        }


    # ------------------------------------------------- #
    #               filter instance seg                 #
    # ------------------------------------------------- #
    pass
 

if __name__ == "__main__":
    main()
