import re
import os
import logging
import sys

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
            parsed_data = [x for x in data.split("\n") if not x.startswith("#")]

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

class Module():
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.package = os.path.basename(os.path.dirname(os.path.dirname(path)))

        self.depends = set()
        self.inherits = set()
        self.names = set()

    def parse_deps(self):
        if not self.depends:
            manifest = literal_eval(read_file(self.path))
            if manifest and "depends" in manifest:
                self.depends = set(manifest.get("depends"))
        return self.depends

    def parse_code(self):
        name_regex = re.compile("[\"']([^\"']*)[\"']")

        inherit_check = re.compile("^ *_inherit *= *[\"'].*[\"'] *$")
        name_check = re.compile("^ *_name *= *[\"'].*[\"'] *$")

        for path in glob(os.path.join(os.path.dirname(self.path), "**/*.py"), recursive=True):
            data = parse_file(path)
            for line in data:
                if re.match(inherit_check, line): #"_inherit =" in line:
                    if "{" not in line and "[" not in line: # one line inherit
                        res = re.search(name_regex, line)
                        if res:
                            self.inherits.add(res.groups()[0])

                    else:
                        pass
                        # TODO: Multiline inheritance
                if re.match(name_check, line):
                    res = re.search(name_regex, line)
                    if res:
                        self.names.add(res.groups()[0])

    #    if self.names and self.inherits:
    #        print(f"{self.name} {self.names} {self.inherits}")

    def validate_names(self, modules):
        for inherit in self.inherits:
            if not self.validate_name(inherit, modules):
                print(f"{self.package} {self.name} missing dependency for {inherit}")

    def validate_name(self, name, modules):
        if name in self.names:
            return True
        for dep in self.depends:
            dep_module = modules.get(dep)
            if dep_module and dep_module.validate_name(name, modules):
                return True
        return False

if __name__ == "__main__":
    modules = {}
    for name, path in find_modules():
        module = Module(name, path)
        modules[name] = module
        module.parse_code()
        module.parse_deps()

    for module in modules.values():
        module.validate_names(modules)
