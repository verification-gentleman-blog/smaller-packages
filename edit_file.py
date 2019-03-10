#!/bin/env python3

import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('r+'))
args = parser.parse_args()

lines = args.file.readlines()
args.file.truncate(0)
args.file.seek(0)
args.file.write('// I made an edit at {}\n'.format(datetime.datetime.now().time()))
for line in lines:
    args.file.write(line)
