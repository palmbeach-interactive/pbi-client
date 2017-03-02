# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import sys
import shutil
from fabric.api import local, lcd, warn_only, env
from fabric.colors import green, red, blue, yellow, cyan
from fabric.operations import prompt

env.warn_only = True

class LocalDeployer(object):

    def __init__(self, key, infrastructure_dir):
        self.key = key
        self.infrastructure_dir = infrastructure_dir

        self.playbook_dir = os.path.join(infrastructure_dir, 'ansible')
        self.playbook_path = os.path.join(self.playbook_dir, self.key.replace('-', '_').replace('.', '_') + '.yml')


        self.update()
        self.self_check()


    def update(self):

        if not os.path.isdir(self.infrastructure_dir):
            raise Exception('infrastructure directory does not exist at {}'.format(self.infrastructure_dir))

        confirm = prompt('Do you want to update your infrastructure repository? Y/n', default='y').lower() == 'y'

        if confirm:
            with lcd(self.infrastructure_dir):
                command = 'git pull origin master'
                local(command)

    def self_check(self):

        if not os.path.isdir(self.playbook_dir):
            raise Exception('ansible/playbook directory does not exist at {}'.format(self.playbook_dir))

        if not os.path.exists(self.playbook_path):
            raise Exception('ansible/playbook file does not exist at {}'.format(self.playbook_path))


        pass


    def run(self, no_input=False):

        with lcd(self.playbook_dir):
            command = 'ansible-playbook -i hosts --tags deploy {playbook_path}'.format(
                playbook_path=self.playbook_path
            )
            local(command)








