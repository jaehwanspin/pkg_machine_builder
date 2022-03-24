#!/usr/bin/python3

import getpass
import os
import re
import json
import yaml
import shutil
import subprocess
import threading

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

def get_source_versions(pakcage_name):
    package_paths = get_package_paths(package_name)
    source_versions = []
    for package_path in package_paths:
        source_version_yml = None
        source_version_yml_path = os.path.join(package_path, "conandata.yml")
        if os.path.exists(source_version_yml_path):
            with open(source_version_yml_path, "r") as f:
                source_version_yml = yaml.safe_load(f)
            source_versions = list(source_version_yml["sources"].keys())
    return source_versions

def get_source_url(pakcage_name, version):
    package_paths = get_package_paths(package_name)
    source_url = ""
    
    for package_path in package_paths:
        source_version_yml = None
        source_version_yml_path = os.path.join(package_path, "conandata.yml")
        if os.path.exists(source_version_yml_path):
            with open(source_version_yml_path, "r") as f:
                source_version_yml = yaml.safe_load(f)
            if source_version_yml["sources"].get(version) is not None:
                if type(source_version_yml["sources"].get(version)) is not list:
                    tmp_url = source_version_yml["sources"][version]["url"]
                    if type(tmp_url) is list:
                        source_url = tmp_url[len(tmp_url) - 1]
                    else:
                        source_url = tmp_url
                else:
                    tmp_url = source_version_yml["sources"][version][0]["url"]
                    if type(tmp_url) is list:
                        source_url = tmp_url[len(tmp_url) - 1]
                    else:
                        source_url = tmp_url
                
    return source_url

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
            dependency_names = re.findall(r'\s{3,4}self.requires\(\"([a-z0-9]+)/\S+\"\)', file_content)

    for dependency_name in dependency_names:
        dependency_names = dependency_names + get_dependencies(dependency_name)

    return dependency_names

def download_source(package_name, version):
    url = get_source_url(package_name, version)
    if url != "":
        print(package_name, version, url)
        tmp = url.split("/")
        wget_cmd = "wget " + url + " -O " + "sources/" + package_name + "/" + version + "/" + tmp[len(tmp) - 1];
        if not os.path.exists("sources/" + package_name + "/" + version + "/" + tmp[len(tmp) - 1]):
            os.system(wget_cmd)

def be_ready_for_source_dir(package_name):
    if not os.path.exists("sources"):
        os.mkdir("sources")
        
    package_source_dir = os.path.join("sources", package_name)
    if not os.path.exists(package_source_dir):
        os.mkdir(package_source_dir)
    
    for version in get_source_versions(package_name):
        version_dir = os.path.join(package_source_dir, version)
        if not os.path.exists(version_dir):
            os.mkdir(version_dir)
        download_source(package_name, version)

def execute_conan_server():
    return subprocess.Popen("gunicorn -b 0.0.0.0:9300 -w 4 -t 300 conans.server.server_launcher:app",
                            stdout=subprocess.PIPE, shell=True)
    

def copy_and_modify_package(package_name):
    # username = getpass.getuser()
    src_dir = os.path.join("conan-center-index/recipes", package_name)
    dst_dir = os.path.join("modified_packages", package_name)
    res = shutil.copytree(src_dir, dst_dir)
    
    for version_dir in get_versions(package_name):
        conandata_yml_path = os.path.join(os.path.join(dst_dir, version_dir), "conandata.yml")
        if os.path.exists(conandata_yml_path):
            conandata_yml = ""
            with open(conandata_yml_path, "rw") as f:
                conandata_yml = yaml.safe_load(f)
                
                
    
    print(res)
    

def start():
    msg = '''
  ____ ___  _   _    _    _   _     ____  _____ ______     _______ ____     ____  _   _ ___ _     ____  _____ ____   
 / ___/ _ \| \ | |  / \  | \ | |   / ___|| ____|  _ \ \   / / ____|  _ \   | __ )| | | |_ _| |   |  _ \| ____|  _ \    
| |  | | | |  \| | / _ \ |  \| |   \___ \|  _| | |_) \ \ / /|  _| | |_) |  |  _ \| | | || || |   | | | |  _| | |_) |     
| |__| |_| | |\  |/ ___ \| |\  |    ___) | |___|  _ < \ V / | |___|  _ <   | |_) | |_| || || |___| |_| | |___|  _ <    
 \____\___/|_| \_/_/   \_\_| \_|   |____/|_____|_| \_\ \_/  |_____|_| \_\  |____/ \___/|___|_____|____/|_____|_| \_\     
'''
    print(msg)

if __name__ == '__main__':
    start()
    
    clone_or_update_conan_center_index()
 
    package_names = load_conan_packages()
    
    for package_name in package_names:
        package_names = package_names + get_dependencies(package_name)
        
    package_names = list(set(package_names))
    
    for package_name in package_names:
        be_ready_for_source_dir(package_name)
    
    conan_server_process = execute_conan_server()
    
    for package_name in package_names:
        copy_and_modify_package(package_name)
    
    conan_server_process.kill()
    
    b = 1
    
    
    
    pass
    