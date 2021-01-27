#!/usr/bin/python3

import os
import json
import logging
import argparse
import subprocess

BUILD_DIR = 'build'
TEMP_DIR = 'tmp'
CODE_DIR = 'code'
TEST_DIR = 'test'
SRC_SUBDIR = 'src'
INC_SUBDIR = 'inc'
LNK_SUBDIR = 'lnk'

GCC = 'gcc'
GPP = 'g++'
AR = 'ar'
LD = 'ld'

VERSION_LATEST = 'latest'

REPO_PATH = "https://github.com/grzegorz-grzeda"

GITIGNORE_LIST = [
    f"{BUILD_DIR}/",
    f"{TEMP_DIR}/"
]

LIBS_TEMPLATE = {
    'libs': [
        {
            "name": "Library name",
            "version": f"Library version (e.g.) {VERSION_LATEST}",
            "repo": f"Repository path if other than {REPO_PATH}/name"
        }
    ]
}

PROJECT_TEMPLATE = {
    "info": {
        "name": "Project name",
        "version": "Project version MAJOR.MINOR.FIX",
        "description": "Description",
        "author": "Author",
        "licence": "Licence name"
    },
    "targets": [
        {
            "arch": "x64",
            "type": [
                "build",
                "test"
            ],
            "prefix": "",
            "location": "",
            "compile_flags": "",
            "link_flags": "",
            "link_script": ""
        }
    ],
    "code": {
        "inc": [],
        "src": []
    },
    "test": {
        "inc": [],
        "src": []
    },
    "libs": []
}


def get_input_for_template(template):
    template = input(template)


def init():
    print("Initing")

    for entry in PROJECT_TEMPLATE['info']:
        PROJECT_TEMPLATE['info'][entry] = input(
            f"{PROJECT_TEMPLATE['info'][entry]}: ")

    with open('project.json', 'w') as project:
        project.write(json.dumps(PROJECT_TEMPLATE, indent=3))

    with open('.gitignore', 'w') as gitignore:
        gitignore.write("\n".join(GITIGNORE_LIST))

    with open('Readme.md', 'w') as readme:
        readme.write(f"# {PROJECT_TEMPLATE['info']['description']}\n")
        readme.write(f"## Version {PROJECT_TEMPLATE['info']['version']}\n")
        readme.write(f"&copy; {PROJECT_TEMPLATE['info']['author']} on {PROJECT_TEMPLATE['info']['licence']} licence\n")

    os.makedirs(f"{CODE_DIR}/{SRC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{CODE_DIR}/{INC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{CODE_DIR}/{LNK_SUBDIR}", exist_ok=True)
    os.makedirs(f"{TEST_DIR}/{SRC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{TEST_DIR}/{INC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{TEST_DIR}/{LNK_SUBDIR}", exist_ok=True)


def add_lib():
    print("Adding library")


def clean():
    print("Cleaning")

    for directory in GITIGNORE_LIST:
        subprocess.call([
            'rm',
            '-rf',
            directory
        ])


def build():
    print("Building")


def test():
    clean()
    build()
    print("Testing")


def parse_args():
    parser = argparse.ArgumentParser(
        description='G2 Package Manager'
    )

    parser.add_argument('action',
                        help='Perform a certain action',
                        choices=get_calls().keys())
    return parser.parse_args()


def get_calls():
    return {
        "init": init,
        "add-library": add_lib,
        "clean": clean,
        "build": build,
        "test": test
    }


def invoke_action(name):
    get_calls()[name]()


def main():
    """ Main routine """

    invoke_action(parse_args().action)


if __name__ == '__main__':
    main()
