# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import os
import logging
import codecs
import shutil
import sys
import time
from redmine import Redmine, ResourceNotFoundError
from fabric.api import local, settings, abort, run, cd, lcd, env, put, hide, prefix, open_shell
from fabric.contrib import files
from fabric.operations import prompt
from logging.config import fileConfig

# TODO: this is hakish...
from .service_api import ApplicationAPIClient

NUM_CHARS = 72
DEFAULT_SLEEP = 10

DEFAULT_SOURCE = 'ssh://git@lab.hazelfire.com/palmbeach/example-com.git'
REDMINE_URL = 'https://lab.hazelfire.com'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

class IncubatorException(Exception):
    pass


class Incubator:

    def __init__(self, key, force_actions, **kwargs):

        if not os.path.isdir(os.path.expanduser('~/code')):
            raise IncubatorException('No "~/code" directory found!')

        self.source = kwargs.get('source')

        self.conf = kwargs.get('conf')

        if self.source:
            name = os.path.basename(self.source)
            if name.endswith('.git'):
                name = name[:-4]

            self.source_key = name.replace('-', '.').replace('_', '.')
        else:
            self.source_key = None

        self.key = key
        self.destination_path = os.path.expanduser(os.path.join('~/code', key))
        self.force_actions = force_actions


        self.redmine_project = None

        # self.redmine_client = None
        # self.redmine_project = None

        log.info('Incubator initialized: {} -> {}'.format(self.source, self.destination_path))

    def selftest(self):
        pass




    def get_redmine_client(self):

        username = os.environ.get('REDMINE_USER')
        password = os.environ.get('REDMINE_PASSWORD')

        if not username:
            username = prompt('redmine user: ')

        if not password:
            password = prompt('redmine password: ')

        self.redmine_client = Redmine(REDMINE_URL, username=username, password=password)

        return self.redmine_client


    def get_redmine_project(self):

        project_id = self.key.replace('.', '-')

        print project_id

        try:
            project = self.redmine_client.project.get(project_id)
        except ResourceNotFoundError as e:

            create = prompt('Project not found on lab. Create it?', default='n').lower()

            parent_id = prompt('Parent project id', default='palmbeach').lower()

            parent = self.redmine_client.project.get(parent_id)

            if create.lower() == 'y':
                project = self.redmine_client.project.new()
                project.name = project_id
                project.identifier = project_id
                project.homepage = 'http://{}'.format(self.key)
                project.is_public = False
                project.parent_id = parent.id
                project.inherit_members = True
                project.enabled_module_names = ['repository', 'gantt']
                project.save()

        pass



    def git_clone(self):
        
        if not self.source:
            raise IncubatorException('clone action requires --source')

        if os.path.isdir(self.destination_path) and not self.force_actions:
            raise IncubatorException('Destination directory {} already exists. Use --force to overwrite.'.format(self.destination_path))

        if os.path.isdir(self.destination_path) and self.force_actions:
            shutil.rmtree(self.destination_path)

        commands = [
            'git clone {source} {destination}'.format(
                source=self.source,
                destination=self.destination_path
            ),
        ]

        for command in commands:
            log.debug('running command: {}'.format(command))
            local(command)


    def git_push(self):

        if not os.path.isdir(self.destination_path):
            raise IncubatorException('Destination directory {} does not exist.'.format(self.destination_path))


        project_id = self.key.replace('.', '-')

        commands = [
            'rm -Rf .git',
            'git init',
            'git remote add origin ssh://git@lab.hazelfire.com/palmbeach/{project_id}'.format(
                project_id=project_id
            ),
            'git add -A',
            'git commit -m "initial commit"',
            'git push origin master',
        ]

        print 'Commands to accept:'
        for command in commands:
            print command

        if prompt('do you want to run these commands?', default='n').lower() == 'y':


            for command in commands:

                with lcd(self.destination_path):
                    log.debug('running command: {}'.format(command))
                    local(command)


    def rename_patterns(self):

        patterns = []
        source_bits = self.source_key.split('.')
        bits = self.key.split('.')

        for char in ['_', '-', '.']:
            patterns.append([char.join(source_bits), char.join(bits)])
            patterns.append([char.join(reversed(source_bits)), char.join(reversed(bits))])

        return patterns


    def replace(self):

        patterns = self.rename_patterns()
        commands = []

        # in-file replacements
        extensions = ('py', 'html', 'txt', 'conf', 'xml', 'scpt', 'iml', 'name', 'md', 'json', 'yaml', 'sh', )
        for pattern in patterns:

            commands.append(
                "find -E {path} -iregex '.*\.({extensions})' -exec sed -i '' s/{src}/{dst}/ {{}} +".format(
                    path = self.destination_path,
                    extensions = '|'.join(extensions),
                    src = pattern[0],
                    dst = pattern[1]
                )
            )


        # file renaming
        for pattern in patterns:

            meta_command = """find {path} -name "*{src}*" -exec sh -c 'echo mv "$1" "$(echo "$1" | sed s/{src}/{dst}/)"' _ {{}} \;""".format(
                    path = self.destination_path,
                    src = pattern[0],
                    dst = pattern[1]
                )
            lines = local(meta_command, capture=True)
            for line in lines.split("\n"):
                if line and not line == '':
                    commands.append(line)

        for command in commands:
            local(command)


    def link_service_project(self):

        if not prompt('do you want to create an application on service.pbi.io?', default='n').lower() == 'y':
            return


        project_id = self.key.replace('.', '-')
        project_key = self.key
        repository = 'ssh://git@lab.hazelfire.com/palmbeach/{project_id}'.format(project_id=project_id)


        api_base_url = self.conf.get('api_url')
        user = self.conf.get('user')
        email = user.get('email')
        api_key = user.get('api_key')

        api_client = ApplicationAPIClient(email, api_key, api_base_url)

        payload = {
            'key': self.key,
            'repository': repository,
        }

        print api_client.create(payload)



    def incubate(self):

        self.redmine_client = self.get_redmine_client()
        self.get_redmine_project()
        self.git_clone()
        self.replace()
        self.git_push()
        self.link_service_project()
