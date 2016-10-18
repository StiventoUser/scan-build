#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.

import os
import argparse
import json
import shlex
import multiprocessing
import subprocess


def run(entry):
    command = shlex.split(entry['command'])
    # do respect 'CC' and 'CXX' environment variables for compiler
    env_name = 'CC' if command[0] == 'cc' else 'CXX'
    if env_name in os.environ:
        command[0] = os.environ[env_name]
    # execute the command in the given directory
    # map exit code to 0/1 to get the correct fail count
    print('exec {0} in {1}'.format(command, entry['directory']))
    return 1 if subprocess.call(command, cwd=entry['directory']) else 0


def main():
    """ Execute compilation commands from a given compilation database. """
    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', type=int, default=1)
    parser.add_argument('cdb', type=argparse.FileType('r'))
    args = parser.parse_args()
    # execute compilation database entry
    failures = 0
    pool = multiprocessing.Pool(args.parallel)
    for current in pool.imap_unordered(run, json.load(args.cdb)):
        failures += current
    pool.close()
    pool.join()
    return failures