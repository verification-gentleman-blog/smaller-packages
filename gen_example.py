#!/bin/env python3

import argparse
import os
import shutil
import stat
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--num-levels', type=int, default=1)
parser.add_argument('--num-packages-per-level', type=int, default=1)
parser.add_argument('--total-num-classes', type=int, default=1000)
args = parser.parse_args()

work_dir = os.path.join('examples', args.name)

shutil.rmtree(work_dir)
os.makedirs(work_dir, exist_ok=True)


class Node(object):

    def __init__(self, name):
        self.name = name
        self.children = []

    def __repr__(self):
        return 'Package {}'.format(self.name)

    def add_child(self, node):
        self.children.append(node)

    def get_children(self):
        return self.children


def add_pkg(level, index=0, parent_id=''):
    if level == 0:
        cur_id = ''
        name = 'p0'
    elif level == 1:
        name = 'p1_{}'.format(index)
        cur_id = index
    else:
        name = "p{}_{}_{}".format(level, parent_id, index)
        cur_id = '{}_{}'.format(parent_id, index)

    node = Node(name)
    if level < args.num_levels - 1:
        for i in range(0, args.num_packages_per_level):
            node.add_child(add_pkg(level + 1, i, cur_id))
    return node


def get_breadth_first_nodes(root):
    nodes = []
    stack = [root]
    while stack:
        cur_node = stack[0]
        stack = stack[1:]
        nodes.append(cur_node)
        for child in cur_node.get_children():
            stack.append(child)
    return nodes


root = add_pkg(0)

for node in get_breadth_first_nodes(root):
    num_classes = int(args.total_num_classes / len(get_breadth_first_nodes(root)))
    gen_cmd = [
        os.path.realpath('gen_package.py'),
        node.name,
        '--num-classes', str(num_classes),
        ]
    for child in node.get_children():
        gen_cmd.extend(['--package-ref', child.name])
    subprocess.check_call(gen_cmd, cwd=work_dir)

compile_script = open(os.path.join(work_dir, 'compile.py'), 'w')
os.chmod(compile_script.name, os.stat(compile_script.name).st_mode | stat.S_IEXEC)
compile_script.write('#!/bin/env python3\n')
compile_script.write('\n')
compile_script.write('import argparse\n')
compile_script.write('import subprocess\n')
compile_script.write('\n')
compile_script.write('parser = argparse.ArgumentParser()\n')
compile_script.write('parser.add_argument(\'--incremental\')\n')
compile_script.write('args = parser.parse_args()\n')
compile_script.write('\n')
compile_script.write('if args.incremental:\n')
compile_script.write('    subprocess.check_call(["{}", args.incremental])\n'.format(
        os.path.realpath('edit_file.py')))
compile_script.write('\n')
compile_script.write('xrun_cmd = [\n')
compile_script.write('    "xrun",\n')
compile_script.write('    "-elaborate",\n')

for node in reversed(get_breadth_first_nodes(root)):
    compile_script.write('    "{}.sv",\n'.format(node.name))

compile_script.write('    ]\n')
compile_script.write('if not args.incremental:\n')
compile_script.write('    xrun_cmd.append("-clean")\n')
compile_script.write('subprocess.check_call(xrun_cmd)')
