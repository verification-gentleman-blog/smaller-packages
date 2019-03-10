#!/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('name',
                    help='name of the package to be generated')
parser.add_argument('--num-classes',
                    type=int,
                    default=1,
                    help='number of class definitions the package will contain')
parser.add_argument('--package-ref',
                    action='append',
                    default=[],
                    help='makes this package depend on the provided package')
args = parser.parse_args()

with open(args.name + '.sv', 'w') as f:
    f.write('package {};\n'.format(args.name))
    f.write('\n')

    if args.package_ref:
        for package_ref in args.package_ref:
            f.write('  import {}::*;\n'.format(package_ref))
        f.write('\n')

    for i in range(0, args.num_classes):
        f.write('  class {}_class{};\n'.format(args.name, i))
        f.write('  endclass\n')
        f.write('\n')

    f.write('endpackage\n')
