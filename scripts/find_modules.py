#!/usr/bin/python3
import re
import os
import logging
import sys

from lxml import etree
from ast import literal_eval
from glob import glob

_logger = logging.getLogger(__file__)

verbose = False
ROOT_PATH = "/usr/share"
REGEXES = ['odoo-*/*/__manifest__.py', 'odooext-*/*/__manifest__.py']
CORE_REGEX = ['core-odoo/addons/*/__manifest__.py']
RECURSIVE_ERROR = set()

def recursive_error(name):
    if name[-1] not in RECURSIVE_ERROR:
        RECURSIVE_ERROR.add(name[-1])
        _logger.error(f"Recursive import error for module {name}")

class FileParser():
    def __init__(self):
        self.parsed_files = {}
        self.read_files = {}
        self.known_fileext = [".xml", '.py']

    def parse_file(self, path):
        _, fileext = os.path.splitext(path)
        if path not in self.parsed_files:
            parsed_data = []
            if fileext in self.known_fileext:
                if fileext == '.py':
                    data = self.read_file(path)
                    parsed_data = [x for x in data.split("\n") if not x.startswith("#")]
                elif fileext == '.xml':
                    try:
                        parsed_data = etree.parse(path)
                        etree.strip_tags(parsed_data, etree.Comment)
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

def find_defining_modules(name, modules):
    for module in modules.values():
        if name in module.names:
            yield module.name



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
#<record id="project_archive"...>
#<field name="inherit_id" ref="project.view_project_kanban" />
        regexes = {}
        regexes["py"] = {}
        regexes["py"]["inherit"] = []
        regexes["py"]["names"] = []

        regexes["xml"] = {}

        regexes["py"]["inherit"].append(re.compile("^ *_inherit *= *[\"']([^\"']*)[\"'] *$"))
        regexes["py"]["inherit"].append(re.compile("^ *comodel_name=[\"']([^\"']*)[\"'].*$"))
        regexes["py"]["inherit"].append(re.compile("^.*request\.env\[[\"']([^\"']*)[\"']\].*$"))
        regexes["py"]["inherit"].append(re.compile("^.*self\.env\[[\"']([^\"']*)[\"']\].*$"))

        regexes["py"]["names"].append(re.compile("^ *_name *= *[\"']([^\"']*)[\"'] *$"))

        for path in glob(os.path.join(os.path.dirname(self.path), "**/*"), recursive=True):
            data = file_parser.parse_file(path)
            _, ext = os.path.splitext(path)
            if ext == ".py":
                self.parse_py(data, regexes["py"])
            elif ext == ".xml":
                self.parse_xml(data, regexes["xml"])

    def parse_py(self, data, regexes):
        for line in data:
            for inherit in regexes["inherit"]:
                if res := re.search(inherit, line):
                    self.inherits.add(res.groups()[0])

            for name in regexes["names"]:
                if res := re.search(inherit, line):
                    self.names.add(res.groups()[0])

    def parse_xml(self, data, regexes):
        if not data:
            return
        self.names.update(f"{self.name}.{x}" for x in data.xpath("//record/@id") if x)
        self.inherits.update(data.xpath("//field[@name='inherit_id']/@ref"))

    def validate_names(self, modules):
        count = 0
        total = len(self.inherits)
        for inherit in self.inherits:
            if not self.validate_name(inherit, modules, history=[], first_call=True):
                count += 1
                message = f"{self.package}/{self.name} missing dependency for {inherit}"
                if verbose:
                    defining_modules = ", ".join(find_defining_modules(inherit, modules))
                    message += f" (defined in modules: [{defining_modules}])"
                print(message)
        return count, total

    def validate_name(self, name, modules, history, first_call=False):
        if name in self.names:
            return True
        if self.name in history:
            recursive_error(history)
            return False
        else:
            history.append(self.name)
        if first_call:
            internal_name = f"{self.name}.{name}"
            if internal_name in self.names:
                return True
        for dep in self.depends:
            dep_module = modules.get(dep)
            if dep_module and dep_module.validate_name(name, modules, history.copy()):
                return True
        return False

if __name__ == "__main__":
    modules = {}
    for name, path in find_modules():
        module = Module(name, path)
        modules[name] = module
        module.parse_code()
        module.parse_deps()

    count = 0
    total = 0
    try:
        with open("modules") as f:
            module_list = (modules[x.strip()] for x in f.read().split("\n") if x.strip())
    except:
        module_list = sorted(modules.values(), key=lambda x: x.package + "_"*100 + x.name)

    for module in module_list:
           dcount, dtotal = module.validate_names(modules)
           count += dcount
           total += dtotal

    print(f"Found {count} errors in {total} checks")
