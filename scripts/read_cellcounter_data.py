'''
This file provides utilities to interact with XML-formatted CellCounter Marker files.
'''

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
import json

def parseCellCounterXML(xmlfile, verbose=False):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    markers_copy = {}
    for marker_type in root.findall('Marker_Data/Marker_Type'):
        if marker_type.find('Marker') is None:
            continue
        marker_id = marker_type[1].text
        col = []
        for marker in marker_type.findall('Marker'):
            # first element is MarkerX, second is MarkerY, and third is MarkerZ (always = 1)
            pos = (int(marker[0].text), int(marker[1].text))
            col.append(pos)
        markers_copy[marker_id] = col
    return markers_copy


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i', '--input',
        help='Path to a single CellCounter Marker file in XML format, or a directory containing multiple marker files.'
    )
    ap.add_argument(
        '-o', '--output',
        required=False,
        help='Path to the output directory'
    )
    args = ap.parse_args()
    input_path = Path(args.input)

    if input_path.is_dir():
        for xmlfile in input_path.glob('*.xml'):
            # here, we find the subject and sample identifiers for BIDS indexing
            useful_part_of_fname = str(xmlfile.stem).split('_')[1]
            parts = useful_part_of_fname.split('-')
            if '2025' in parts[0]:
                sub = parts[1]
            else:
                sub = parts[0]
            sample = parts[-1]
            if sample == '8000X':
                sample = 1

            data = parseCellCounterXML(xmlfile)

            base_output_path = Path(args.output) if args.output else Path('compressed_keypoints')
            base_output_path.mkdir(exist_ok=True)
            fname = f'sub-{sub}_sample-{str(sample).zfill(4)}_keypoints.json'
            output_path = base_output_path / fname
            with open(output_path, 'w') as outfile:
                json.dump(data, outfile, indent=4)
    else:
        data = parseCellCounterXML(input_path, verbose=True)
