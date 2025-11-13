'''
This script takes as input 3 things:
- a folder with semantic segmentations (output of a segmentation network)
- a folder with manual counts (in XML format)
- a 'subj_list.txt' file listing the subjects to process

Author: Armand Collin
'''

from pathlib import Path
from AxonDeepSeg.morphometrics import launch_morphometrics_computation
import argparse

# this pixel resolution is specific to the project with APP-cKO mice
PX_SIZE = 0.005648  # in microns (5.648 nm)


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
    
    #TODO: if no axonmyelin mask is found, create them

    # ---------------------------------------------
    # compute morphometrics (myelinated axons)
    # ---------------------------------------------
    argv = [
        '-i', str(seg_dir), 
        '-s', PX_SIZE,
        '-c', 
    ]
        

    # ---------------------------------------------
    # compute morphometrics (unmyelinated axons)
    # ---------------------------------------------
    argv = [
        '-i', str(seg_dir),
        '-s', PX_SIZE,
        '-u',
    ]



if __name__ == "__main__":
    main()
