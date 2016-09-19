# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import sys
import yaml
from fabric.colors import green, red, blue, yellow, cyan
from fabric.api import local, lcd, warn_only, env
from fabric.operations import prompt
from .util import colors

from .settings import PBI_PROJECT_CONFIG_FILE

class ClientHandler:

    def __init__(self, *args, **kwargs):
        infrastructure_dir = kwargs['conf'].get('infrastructure')

        self.infrastructure_dir = os.path.expanduser(infrastructure_dir) if infrastructure_dir else None
        self.playbook_dir = os.path.join(self.infrastructure_dir, 'ansible')

        if not os.path.isdir(self.playbook_dir):
            raise Exception('ansible/playbook directory does not exist at {}'.format(self.playbook_dir))


    def update(self):

        if prompt('Update pbi client? Y/n', default='n').lower() == 'y':
            print(cyan('You likely will be promted to enter your root password.'))
            command = 'sudo pip install -I -e "git+https://github.com/palmbeach-interactive/pbi-client.git#egg=pbi-client"'
            local(command)
            sys.exit(0)


        if prompt('Update infrastructure repository? Y/n', default='y').lower() == 'y':
            print(cyan('Updating infratsructure repository'))

            with lcd(self.infrastructure_dir):
                command = 'git pull origin master'
                local(command)

        if prompt('Install ansible requirements? Y/n', default='y').lower() == 'y':
            print(cyan('installing ansible requirements'))

            with lcd(self.playbook_dir):
                command = 'ansible-galaxy install -f -r requirements.yml'
                local(command)









        pass