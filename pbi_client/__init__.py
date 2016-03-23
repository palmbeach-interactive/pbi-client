#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'

import argparse
import os
from incubator import Incubator
from infrastructure import ApplicationHandler
from configobj import ConfigObj

DEFAULT_SOURCE = 'ssh://git@lab.hazelfire.com/palmbeach/example-com.git'


usage="""
----------------------------------------------------------------
PBI.IO - CLI tool
----------------------------------------------------------------
    pbi list
    pbi example.com info
    pbi example.com deploy
    pbi example.com incubate
----------------------------------------------------------------
"""

epilog="""
- pbi.io -------------------------------------------------------
"""




def main():
    parser = argparse.ArgumentParser(usage=usage, epilog=epilog)

    parser.add_argument(
        'base',
        metavar='<domain.tld> <action>',
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
        action = base[0]
        key = None
    elif len(base) == 2:
        action = base[1]
        key = base[0]

    if action in ['deploy', 'info', 'list', 'check']:
        handler = ApplicationHandler(key, **args_dict)
        getattr(handler, action)()

    if action in ['incubate',]:

        print '*****'

        handler = Incubator(key, **args_dict)
        getattr(handler, action)()

