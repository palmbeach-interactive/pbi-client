#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.5'

import argparse
import os
import sys
import yaml
from incubator import Incubator
from client import ClientHandler
from infrastructure import ApplicationHandler
from configobj import ConfigObj
from check import self_check

from settings import DEFAULT_SOURCE, PBI_PROJECT_CONFIG_FILE


usage="""
----------------------------------------------------------------
PBI.IO - CLI tool - v{version}
----------------------------------------------------------------
    pbi list
    pbi update
    pbi info (example.com)
    pbi deploy (example.com)
    pbi incubate (example.com) - initialize a project
    pbi create-project (example.com) - create a project on service.pbi.io
    pbi create-application (example.com) - create a application on service.pbi.io
    pbi install (example.com) - local project installaton
    pbi load (example.com) - load tmux session
----------------------------------------------------------------
""".format(version=__version__)

epilog="""
- pbi.io -------------------------------------------------------
"""




def main():

    self_check()

    parser = argparse.ArgumentParser(usage=usage, epilog=epilog)

    parser.add_argument(
        'base',
        metavar='<action> <domain.tld>',
        nargs='+',
        help='Base command',
    )
    parser.add_argument(
        '-s', '--source',
        dest='source',
        metavar='PATH',
        help='Source path',
        default=DEFAULT_SOURCE,
        required=False
    )
    parser.add_argument(
        '--config',
        dest='config_file',
        metavar='PATH',
        help='Config file path',
        default=os.path.expanduser('~/.pbi.cfg'),
        required=False
    )
    parser.add_argument(
        '-i', '--init',
        dest='init',
        help='Initialize project',
        action='store_true',
    )
    parser.add_argument(
        '-c', '--check',
        dest='check',
        help='Check project',
        action='store_true',
    )
    parser.add_argument(
        '--force',
        dest='force_actions',
        action='store_true',
        help='Force overrides',
    )

    args = parser.parse_args()
    args_dict = args.__dict__

    config_file = args_dict['config_file']
    if not os.path.isfile(config_file):
        raise IOError('Unable to read config file: {}'.format(config_file))

    conf = ConfigObj(os.path.expanduser('~/.pbi.cfg'))

    args_dict['conf'] = conf

    base = args_dict['base']
    if len(base) == 1:
        action = base[0].replace('-', '_')
        key = None
    elif len(base) == 2:
        action = base[0].replace('-', '_')
        key = base[1]


    # check for config file (.pbi.yaml)
    args_dict['project'] = None
    if os.path.exists(PBI_PROJECT_CONFIG_FILE):
        stream = open(PBI_PROJECT_CONFIG_FILE, "r")
        args_dict['project'] = yaml.load(stream)
        key = args_dict['project'].get('key')

    if action in ['init',] and key:
        if os.path.exists(PBI_PROJECT_CONFIG_FILE):
            raise EnvironmentError(
                'Configuration file already exists: {0}. You have to delete it first in order to run "init" again'.format(
                    PBI_PROJECT_CONFIG_FILE))
        else:
            raise EnvironmentError('You have to run "init" in the project directory, without specifying a key.')

    if action in ['init', 'deploy', 'info', 'list', 'check', 'install', 'load', 'create_project', 'create_application']:
        handler = ApplicationHandler(key, **args_dict)
        getattr(handler, action)()

    if action in ['incubate',]:

        handler = Incubator(key, **args_dict)
        getattr(handler, action)()

    if action in ['update',]:

        handler = ClientHandler(**args_dict)
        getattr(handler, action)()

