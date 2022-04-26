import re
import os
import logging

from ast import literal_eval
from glob import glob

_logger = logging.getLogger(__file__)


ROOT_PATH = "/usr/share"
REGEXES = ['odoo-*/*/__manifest__.py', 'odooext-*/*/__manifest__.py']
CORE_REGEX = ['core-odoo/addons/*/__manifest__.py']


PARSED_FILES = {}
def parse_file(path):
    if path not in PARSED_FILES:
        _, fileext = os.path.splitext(path)
        data = read_file(path)
        parsed_data = []
        if fileext == '.py':
            parsed_data = [x for x in data if not x.startswith("#")]

        PARSED_FILES[path] = parsed_data
    return PARSED_FILES.get(path)

READ_FILES = {}
def read_file(path):
    if path not in READ_FILES:
        with open(path) as f:
            READ_FILES[path] = f.read()
    return READ_FILES.get(path)


def find_modules(root_directory=ROOT_PATH, include_core=True):
    for regex in REGEXES + CORE_REGEX:
        path = os.path.join(ROOT_PATH, regex)
        for manifest_path in glob(path):
            module_name = os.path.basename(os.path.dirname(manifest_path))
            yield module_name, manifest_path

def parse_deps(manifest_path):
    manifest = literal_eval(read_file(manifest_path))
    if manifest and "depends" in manifest:
        return manifest.get("depends")

def parse_code(manifest_path):
    for path in glob(os.path.join(os.path.dirname(manifest_path), "**/*.py"), recursive=True):
        print(f"{path=}")
        data = parse_file(path)
        for line in data:
            if "_inherit" in data:
                print(f"{line=}")



if __name__ == "__main__":
    for name, path in find_modules():
#        print(f"{name=} {path=} {parse_deps(path)=}")
        print(f"{name=}")
        parse_code(path)

