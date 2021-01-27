#!/usr/bin/python3

import os
import json
import logging
import argparse
import subprocess

PROJECT_FILE = 'project.json'

BUILD_DIR = 'build'
TEMP_DIR = 'tmp'
CODE_DIR = 'code'
TEST_DIR = 'test'
LIBS_DIR = 'libs'
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
    LIBS_DIR: [
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
            "prefix": "",
            "location": "",
            "compile_flags": "",
            "link_flags": "",
            "link_script": ""
        }
    ],
    CODE_DIR: {
        INC_SUBDIR: [],
        SRC_SUBDIR: []
    },
    TEST_DIR: {
        INC_SUBDIR: [],
        SRC_SUBDIR: []
    },
    LIBS_DIR: []
}


def get_input_for_template(template):
    template = input(template)


def init():
    logging.info("Initing")

    for entry in PROJECT_TEMPLATE['info']:
        PROJECT_TEMPLATE['info'][entry] = input(
            f"{PROJECT_TEMPLATE['info'][entry]}: ")

    with open(PROJECT_FILE, 'w') as project:
        project.write(json.dumps(PROJECT_TEMPLATE, indent=3))

    with open('.gitignore', 'w') as gitignore:
        gitignore.write("\n".join(GITIGNORE_LIST))

    with open('Readme.md', 'w') as readme:
        readme.write(f"# {PROJECT_TEMPLATE['info']['description']}\n")
        readme.write(f"## Version {PROJECT_TEMPLATE['info']['version']}\n")
        readme.write(
            f"&copy; {PROJECT_TEMPLATE['info']['author']} on {PROJECT_TEMPLATE['info']['licence']} licence\n")

    os.makedirs(f"{CODE_DIR}/{SRC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{CODE_DIR}/{INC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{CODE_DIR}/{LNK_SUBDIR}", exist_ok=True)
    os.makedirs(f"{TEST_DIR}/{SRC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{TEST_DIR}/{INC_SUBDIR}", exist_ok=True)
    os.makedirs(f"{TEST_DIR}/{LNK_SUBDIR}", exist_ok=True)


def add_lib():
    logging.info("Adding library")


def install_lib():
    logging.info("Installing libraries")

    logging.debug(f"Removing {LIBS_DIR}")
    subprocess.run(['rm -rf', LIBS_DIR])

    # open project.json
    # read libs
    # for each lib
    # - git clone the lib
    # - git checkout to the specified version


def clean():
    logging.info("Cleaning")

    for directory in GITIGNORE_LIST:
        subprocess.run([
            'rm',
            '-rf',
            directory
        ])


def build(remove_temp=True):
    try:
        with open(PROJECT_FILE) as project_file:
            settings = json.load(project_file)
            name = settings['info']['name']
            architectures = settings['targets']
            includes = settings['code']['inc']
            sources = settings['code']['src']

            include_dirs = list(set([
                os.path.join(
                    CODE_DIR,
                    INC_SUBDIR,
                    os.path.dirname(inc)
                ) for inc in includes
            ]))

            for architecture in architectures:
                arch_name = architecture['arch']
                logging.info(f"Building architecture ({arch_name})")
                objects = [
                    (
                        os.path.join(TEMP_DIR, arch_name, CODE_DIR,
                                     SRC_SUBDIR, f"{source}.o"),
                        os.path.join(CODE_DIR, SRC_SUBDIR, source)
                    ) for source in sources
                ]

                obj_dirs = list(set([os.path.dirname(obj[0])
                                     for obj in objects]))
                for obj_dir in obj_dirs:
                    logging.debug(f"Creating directory {obj_dir}")
                    os.makedirs(obj_dir, exist_ok=True)

                # Add compilation of fetched libraries

                for obj in objects:
                    logging.info(f"Compiling ({arch_name}) {obj[1]}")

                    cc = [GCC]

                    for inc in include_dirs:
                        cc.append(f'-I{inc}')

                    cc.extend([
                        '-c',
                        obj[1],
                        '-o',
                        obj[0]
                    ])

                    logging.debug(f'Executing "{" ".join(cc)}"')
                    subprocess.run(cc, cwd=os.getcwd(),
                                   stderr=subprocess.STDOUT)

                cc = [GCC]
                cc.extend([obj[0] for obj in objects])

                exe_name = os.path.join(BUILD_DIR, arch_name, name)
                cc.extend(['-o', exe_name])

                logging.info(f"Linking ({arch_name}) {exe_name}")
                logging.debug(
                    f"Creating directory {os.path.dirname(exe_name)}")
                os.makedirs(os.path.dirname(exe_name), exist_ok=True)

                logging.debug(f'Executing "{" ".join(cc)}"')
                subprocess.run(cc, cwd=os.getcwd(), stderr=subprocess.STDOUT)

            if remove_temp:
                logging.debug(f'Removing temporaty {TEMP_DIR}/ directory')
                subprocess.run(['rm', '-rf', TEMP_DIR])

    except FileNotFoundError:
        logging.error(f"{PROJECT_FILE} does not exist. Initialise the project!")


def test():
    clean()
    build()  # build without removing temp dir

    # open project.json and fetch content
    # compose list of architectures
    # compose list of test include dirs
    # compose list of test sources
    # for each architecure
    # compile test sources (depending on architecture setting) with build sources
    # link
    # run
    # remowe temp dir
    print("Testing")


def parse_args():
    parser = argparse.ArgumentParser(
        description='G2 Package Manager'
    )

    parser.add_argument('action',
                        help='Perform a certain action',
                        choices=get_calls().keys())
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')
    return parser.parse_args()


def get_calls():
    return {
        "init": init,
        "add-library": add_lib,
        "install-libraries": install_lib,
        "clean": clean,
        "build": build,
        "test": test
    }


def invoke_action(name):
    get_calls()[name]()


def main():
    """ Main routine """
    args = parse_args()

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=logging.DEBUG if args.verbose == True else logging.INFO)

    invoke_action(args.action)


if __name__ == '__main__':
    main()
