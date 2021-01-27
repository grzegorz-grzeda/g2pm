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
LIBS_DIR = 'libs'
PLAT_DIR = 'platforms'
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
    PLAT_DIR: [
        {
            "name": "x64",
            "compiler_prefix": "",
            "compiler_location": "",
            "compile_flags": "",
            "link_flags": "",
            LNK_SUBDIR: "",
            INC_SUBDIR: [],
            SRC_SUBDIR: []
        }
    ],
    CODE_DIR: {
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

    for platform in PROJECT_TEMPLATE[PLAT_DIR]:
        os.makedirs(os.path.join(
            PLAT_DIR, platform['name'], SRC_SUBDIR), exist_ok=True)
        os.makedirs(os.path.join(
            PLAT_DIR, platform['name'], INC_SUBDIR), exist_ok=True)


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
            platforms = settings[PLAT_DIR]
            includes = settings[CODE_DIR][INC_SUBDIR]
            sources = settings[CODE_DIR][SRC_SUBDIR]

            include_dirs = list(set([
                os.path.join(
                    CODE_DIR,
                    INC_SUBDIR,
                    os.path.dirname(inc)
                ) for inc in includes
            ]))

            for platform in platforms:
                platform_name = platform['name']
                logging.info(f"Building platform ({platform_name})")
                objects = [
                    (
                        os.path.join(TEMP_DIR, platform_name, CODE_DIR,
                                     SRC_SUBDIR, f"{source}.o"),
                        os.path.join(CODE_DIR, SRC_SUBDIR, source)
                    ) for source in sources
                ]

                objects.extend([
                    (
                        os.path.join(TEMP_DIR, platform_name,
                                     PLAT_DIR, SRC_SUBDIR, f"{source}.o"),
                        os.path.join(PLAT_DIR, platform_name,
                                     SRC_SUBDIR, source)
                    ) for source in platform[SRC_SUBDIR]
                ])

                obj_dirs = list(set([os.path.dirname(obj[0])
                                     for obj in objects]))
                for obj_dir in obj_dirs:
                    logging.debug(f"Creating directory {obj_dir}")
                    os.makedirs(obj_dir, exist_ok=True)

                # Add compilation of fetched libraries

                for obj in objects:
                    logging.info(f"Compiling ({platform_name}) {obj[1]}")

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

                exe_name = os.path.join(BUILD_DIR, platform_name, name)
                cc.extend(['-o', exe_name])

                logging.info(f"Linking ({platform_name}) {exe_name}")
                logging.debug(
                    f"Creating directory {os.path.dirname(exe_name)}")
                os.makedirs(os.path.dirname(exe_name), exist_ok=True)

                logging.debug(f'Executing "{" ".join(cc)}"')
                subprocess.run(cc, cwd=os.getcwd(), stderr=subprocess.STDOUT)

            if remove_temp:
                logging.debug(f'Removing temporaty {TEMP_DIR}/ directory')
                subprocess.run(['rm', '-rf', TEMP_DIR])

    except FileNotFoundError:
        logging.error(
            f"{PROJECT_FILE} does not exist. Initialise the project!")


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
        "build": build
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
