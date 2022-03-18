#!/usr/bin/python3
import glob
import os
import json
import sys

from collections import defaultdict

calc_tree = defaultdict(int)
root_dir = "/usr/share"


def _find_manifests(directory):
    files = []
    for file in glob.iglob(os.path.join(directory, '**/__manifest__.py'), recursive=True):
        files.append(file)
    return files


def _read_manif(path):
    module = path.split("/")[-2]
    mod_path = "/".join(path.split("/")[:-1])
    with open(path) as f:
        rows = f.read().split("\n")
    cleaned = "".join([row.split("#")[0] for row in rows if not row.strip().startswith("#")])
    cleaned = cleaned.replace("\t", " ").replace("'", '"')
    old_cleaned = None

    while old_cleaned != cleaned:
        old_cleaned = cleaned
        cleaned = cleaned.replace("  ", " ")

    try:
        i = cleaned.index("\"depends")
        if i > 0:
            cleaned = cleaned[i:]
        i = cleaned.index("]")
        if i > 0:
            cleaned = cleaned[:i+1]
        i = cleaned.index("[")
        if i > 0:
            cleaned = cleaned[i:]
        return mod_path, module, eval(cleaned)
    except ValueError:
        return mod_path, module, []


def find_tree(struc, module, depth=0):
    missing = set()
    if module not in struc:
        missing.add(module)
    else:
        path = struc[module][0]
        dep = struc[module][1]
        space = "    " * depth
        print(f"{space}{module}")
        for x in dep:
            calc_tree[x] = max(depth, calc_tree[x])
            missing.update(find_tree(struc, x, depth+1))

    if depth == 0 and missing:
        print("Missing modules:")
        print("\n".join(missing))
    return missing


def rev_tree(struc, i=None, prev=None, depth=0):
    space = depth * "    "
    if depth == 0:
        i = sorted(set(calc_tree.values()), reverse=True)[0]

    for k, v in calc_tree.items():
        if v != i:
            continue
        if prev is None or k in struc and prev in struc[k][1]:
            print(f"{space}{k}")
            rev_tree(struc, i-1, k, depth+1)
        #print(struc[k])



def pop_tree(root_dir):
    manifest_files = _find_manifests(root_dir)

    d = {}
    for f in manifest_files:
        p, a, b = _read_manif(f)
        d[a] = (p, b)
    return d

if __name__ == '__main__':
    module = sys.argv[1]
    tree = pop_tree(root_dir)
    find_tree(tree, module)

