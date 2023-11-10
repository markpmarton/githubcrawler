#!../venv/bin/python

import os
import json
from argparse import ArgumentParser
from ghcrawler import GhCrawler

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="in_path", help="Full path of the input Json config file", required=True)
    parser.add_argument("-o", "--output", dest="out_path", help="Path to store the results", required=False)
    args = parser.parse_args()
    
    if os.path.isfile(args.in_path):
        inp_dict = {}
        with open(args.in_path) as reader:
            inp_dict = json.load(reader)
        GhCrawler(inp_dict, out_path=args.out_path).run()

