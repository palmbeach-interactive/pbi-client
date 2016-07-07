# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import yaml
from fabric.colors import green, red, blue, yellow, cyan
from fabric.operations import prompt
from .service_api import ApplicationAPIClient
from .installer import LocalInstaller
from .util import colors

from .settings import PBI_PROJECT_CONFIG_FILE


def colorize(line, color=colors.BOLD):
    return color + line + colors.ENDC


class ApplicationHandler:

    def __init__(self, key=None, *args, **kwargs):

        self.key = key

        workspace_dir = kwargs['conf'].get('workspace')
        virtualenv_dir = kwargs['conf'].get('virtualenv')

        if not workspace_dir:
            raise IOError('workspace not configured')

        self.workspace_dir = os.path.expanduser(workspace_dir)
        self.virtualenv_dir = os.path.expanduser(virtualenv_dir) if virtualenv_dir else None

        api_base_url = kwargs['conf'].get('api_url')

        user = kwargs['conf'].get('user')
        if not user:
            raise IOError('user not configured')

        email = user.get('email')
        api_key = user.get('api_key')

        self.api_client = ApplicationAPIClient(email, api_key, api_base_url)

    def check(self):

        result = self.api_client.check_version()

        pass


    def list(self):

        result = self.api_client.list()

        for application in result['objects']:
            print((green(':' * 72)))
            print('key:        {}'.format(application['key']))
            print('uuid:       {}'.format(application['uuid']))
            print('repository: {}'.format(application['repository']))
            print('branch:     {}'.format(application['repository_branch']))
            print('website:    {}'.format(application['website']))
            print('admin:      {}'.format(application['website_admin']))
            print('')

        print('')

    def info(self):

        application = self.api_client.detail(self.key)

        print((green(':' * 72)))
        print('key:             {}'.format(application['key']))
        print('uuid:            {}'.format(application['uuid']))
        print('repository:      {}'.format(application['repository']))
        print('branch:          {}'.format(application['repository_branch']))
        print('website:         {}'.format(application['website']))
        print('admin:           {}'.format(application['website_admin']))

        local_path = os.path.join(self.workspace_dir, application['key'])
        if not os.path.isdir(local_path):
            print(yellow('local workspace: {} [MISSING]'.format(local_path)))
        else:
            print(green('local workspace: {} [OK]'.format(local_path)))

    def init(self):

        # get key from directory
        cwd = os.getcwd()
        project_dir = os.path.basename(cwd)
        key = project_dir.strip()
        local_path = os.path.join(self.workspace_dir, key)

        print((green(':' * 72)))
        print('key:             {}'.format(key))
        print('local path:      {}'.format(local_path))
        print('')

        confirm = prompt(
            'Looks correct? Do you want to add "{0}" config file? y/n'.format(PBI_PROJECT_CONFIG_FILE), default='n'
        ).lower() == 'y'

        if confirm:
            project_settings = {
                'key': key
            }
            with open(PBI_PROJECT_CONFIG_FILE, 'w') as outfile:
                outfile.write(yaml.safe_dump(project_settings, default_flow_style=False))

    def deploy(self):

        deployer = self.api_client.get_deployer(self.key)

        print((green(':' * 72)))
        print('uuid:            {}'.format(deployer['uuid']))
        print('status:          {}'.format(deployer['status']))
        print('playbook:        {}'.format(deployer['playbook']))
        print('inventory:       {}'.format(deployer['inventory']))
        print('limit:           {}'.format(deployer['limit']))
        print('')

        confirm = prompt('Do you want to continue? y/n', default='n').lower() == 'y'

        if confirm:
            result = self.api_client.deploy_run(deployer)

    def install(self):

        application = self.api_client.detail(self.key)


        print((green(':' * 72)))
        print('key:             {}'.format(application['key']))
        print('uuid:            {}'.format(application['uuid']))
        print('repository:      {}'.format(application['repository']))

        installer = LocalInstaller(
            key=application['key'],
            repository=application['repository'],
            workspace_dir = self.workspace_dir,
            virtualenv_dir = self.virtualenv_dir,
        )


        installer.run()

        # local_path = os.path.join(self.workspace_dir, application['key'])
        # if not os.path.isdir(local_path):
        #     print(yellow('local workspace: {} [MISSING]'.format(local_path)))
        # else:
        #     print(green('local workspace: {} [OK]'.format(local_path)))

