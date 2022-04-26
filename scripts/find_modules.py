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


class FileParser():
    def __init__(self):
        self.parsed_files = {}
        self.read_files = {}
        self.known_fileext = ['.py', '.xml']

    def parse_file(self, path):
        _, fileext = os.path.splitext(path)
        if path not in self.parsed_files:
            parsed_data = []
            if fileext in self.known_fileext:
                data = self.read_file(path)
                if fileext == '.py':
                    parsed_data = [x for x in data.split("\n") if not x.startswith("#")]
                elif fileext == '.xml':
                    try:
                        from lxml import etree
                        tree = etree.fromstring(data)
                        etree.strip_tags(tree, etree.Comment)
                        parsed_data = etree.tostring(tree).decode("utf-8").split("\n")
#                        parsed_data = str(etree.tostring(tree, encoding="utf8")).split("\n")

                    except Exception as e:
                        pass #_logger.error(f"Error reading file {path}: {e}")
            self.parsed_files[path] = parsed_data
        return self.parsed_files.get(path)

    def read_file(self, path):
        if path not in self.read_files:
            try:
                with open(path) as f:
                    self.read_files[path] = f.read()
            except Exception as e:
                _logger.error(f"Error reading file {path}: {e}")
        return self.read_files.get(path)

file_parser = FileParser()


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
            manifest = literal_eval(file_parser.read_file(self.path))
            if manifest and "depends" in manifest:
                self.depends = set(manifest.get("depends"))
        return self.depends

    def parse_code(self):
        name_regex = re.compile("[\"']([^\"']*)[\"']")

        inherit_check = re.compile("^ *_inherit *= *[\"'].*[\"'] *$")
        name_check = re.compile("^ *_name *= *[\"'].*[\"'] *$")

        for path in glob(os.path.join(os.path.dirname(self.path), "**/*"), recursive=True):
            data = file_parser.parse_file(path)
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
