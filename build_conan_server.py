#!/usr/bin/python3

import sys
import os
import re
import json
import yaml

def clone_or_update_conan_center_index():
    if not os.path.exists("conan-center-index"):
        os.system("/bin/bash -c \"git clone https://github.com/conan-io/conan-center-index\"")
    else:
        os.chdir("conan-center-index")
        os.system("/bin/bash -c \"git pull\"")
        os.chdir("..")

def get_package_paths(package_name):
    package_paths = []
    version_yml = None
    version_yml_path = os.path.join(
        os.path.join("conan-center-index/recipes", package_name),
        "config.yml")
    with open(version_yml_path, "r") as f:
        version_yml = yaml.safe_load(f)

    for version in version_yml["versions"]:
        package_paths.append(os.path.join(os.path.dirname(version_yml_path),
                             version_yml["versions"][version]["folder"]))
        
    return list(set(package_paths))

def get_versions(package_name):
    versions = []
    version_yml = None
    version_yml_path = os.path.join(
        os.path.join("conan-center-index/recipes", package_name),
        "config.yml")
    with open(version_yml_path, "r") as f:
        version_yml = yaml.safe_load(f)
    
    for version in version_yml["versions"]:
        versions.append(str(version))
    return versions

def load_conan_packages():
    package_names = []
    with open("conan_packages.json", "r") as f:
        package_names = json.load(f)["packages"]
    return package_names

def get_dependencies(package_name):
    dependency_names = []
    for package_path in get_package_paths(package_name):
        conanfile_py_path = os.path.join(package_path, "conanfile.py")
        with open(conanfile_py_path, "r") as f:
            file_content = f.read()
            dependency_names = re.findall(r'self.requires\(\"([a-z0-9]+)/\S+\"\)', file_content)

    for dependency_name in dependency_names:
        dependency_names = dependency_names + get_dependencies(dependency_name)

    return dependency_names

def download_sources(package_name, version):

    pass

def be_ready_for_source_dir(package_name):
    if not os.path.exists("sources"):
        os.mkdir("sources")
        
    package_source_dir = os.path.join("sources", package_name)
    if not os.path.exists(package_source_dir):
        os.mkdir(package_source_dir)
    
    for version in get_versions(package_name):
        version_dir = os.path.join(package_source_dir, version)
        if not os.path.exists(version_dir):
            os.mkdir(version_dir)
            
    
    
    pass

if __name__ == '__main__':
    clone_or_update_conan_center_index()
 
    package_names = load_conan_packages()
    
    for package_name in package_names:
        package_names = package_names + get_dependencies(package_name)
        
    package_names = list(set(package_names))
    
        
    
    b = 1
    
    pass
    