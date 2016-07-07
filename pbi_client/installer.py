# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import sys
import shutil
from fabric.api import local, lcd, warn_only, env
from fabric.colors import green, red, blue, yellow, cyan
from fabric.operations import prompt

DEFAULT_DATABASE_USER = 'root'
DEFAULT_DATABASE_PASSWORD = 'root'
MYSQL_ADMIN_COMMAND = 'mysqladmin5'

env.warn_only = True

class LocalInstaller(object):

    def __init__(self, key, repository, workspace_dir, virtualenv_dir):

        self.key = key
        self.repository = repository
        self.workspace_dir = workspace_dir
        self.virtualenv_dir = virtualenv_dir

        print((green(':' * 72)))
        print('workspace_dir:   {}'.format(self.workspace_dir))
        print('virtualenv_dir:  {}'.format(self.virtualenv_dir))

        if not self.workspace_dir or not os.path.isdir(self.workspace_dir):
            raise IOError('Specified "workspace" is not a directory: {0}'.format(self.workspace_dir))

        if not self.virtualenv_dir or not os.path.isdir(self.virtualenv_dir):
            raise IOError('Specified "virtualenv" is not a directory: {0}'.format(self.virtualenv_dir))


    def run(self, no_input=False):

        local_path = os.path.join(self.workspace_dir, self.key)
        virtualenv = os.path.join(self.virtualenv_dir, self.key)
        branch = 'master'
        db_name = self.key

        db_name = self.key.split('.')
        db_name.reverse()
        db_name = '_'.join(db_name) + '_local'

        if os.path.exists(local_path):
            print((yellow(':' * 72)))
            print(yellow('local path exists: {0}'.format(local_path)))
            if prompt('Delete path to continue? y/n', default='n').lower() == 'y':
                shutil.rmtree(local_path)
            else:
                pass
                #sys.exit(1)

        if os.path.exists(virtualenv):
            print((yellow(':' * 72)))
            print(yellow('virtualenv path exists: {0}'.format(virtualenv)))
            if prompt('Delete path to continue? y/n', default='n').lower() == 'y':
                shutil.rmtree(virtualenv)
            else:
                pass
                #sys.exit(1)

        print((cyan(':' * 72)))
        print(cyan('checkout {0}@{1} to {2}'.format(self.repository, branch, local_path)))
        if prompt('Continue? y/n', default='y').lower() == 'y':
            checkout = self.checkout_code(repository=self.repository, branch=branch, local_path=local_path)

        print((cyan(':' * 72)))
        print(cyan('install requirements to {0}'.format(virtualenv)))
        if prompt('Continue? y/n', default='y').lower() == 'y':
            requirements = self.install_virtualenv(local_path=local_path, virtualenv=virtualenv)

        print((cyan(':' * 72)))
        print(cyan('create local database {0}'.format(db_name)))
        if prompt('Continue? y/n', default='y').lower() == 'y':
            database = self.create_database(db_name=db_name)

        print((cyan(':' * 72)))
        print(cyan('install local settings'))
        if prompt('Continue? y/n', default='y').lower() == 'y':
            local_settings = self.install_local_settings(local_path=local_path)

        print((cyan(':' * 72)))
        print(cyan('run database migrations'))
        if prompt('Continue? y/n', default='y').lower() == 'y':
            migrate = self.run_migrations(local_path=local_path, virtualenv=virtualenv)

        if os.path.exists(os.path.join(local_path, 'packages.json')):
            print((cyan(':' * 72)))
            print(cyan('install npm packages'))
            if prompt('Continue? y/n', default='y').lower() == 'y':
                migrate = self.install_npm_packages(local_path=local_path)

        if os.path.exists(os.path.join(local_path, '.tmuxp.yaml')):
            print((cyan(':' * 72)))
            print(cyan('run tmux session'))
            if prompt('Continue? y/n', default='y').lower() == 'y':
                tmux = self.run_tmuxp(local_path=local_path)






    def checkout_code(self, repository, local_path, branch):

        command = 'git clone {0} {1}'.format(repository, local_path)
        local(command)

        with lcd(local_path):
            command = 'git checkout {0}'.format(branch)
            local(command)

        return os.path.isdir(local_path)


    def install_virtualenv(self, local_path, virtualenv):

        virtualenv_bin = os.path.join(virtualenv, 'bin')
        command = 'virtualenv {0}'.format(virtualenv)
        local(command)

        with lcd(local_path):

            if os.path.exists('requirements.txt'):
                requirements_path = 'requirements.txt'
            else:
                requirements_path = os.path.join('website', 'requirements', 'requirements.txt')

            if not os.path.exists(requirements_path):
                raise IOError('requirements.txt does not exist: {}'.format(requirements_path))

            command = '{0} install -r {1}'.format(os.path.join(virtualenv_bin, 'pip'), requirements_path)
            local(command)

        return os.path.isdir(virtualenv)

    def create_database(self, db_name, user=DEFAULT_DATABASE_USER, password=DEFAULT_DATABASE_PASSWORD):

        command = '{0} -u {1} -p{2} create {3}'.format(MYSQL_ADMIN_COMMAND, user, password, db_name)

        with warn_only():
            local(command)


    def install_local_settings(self, local_path):

        with lcd(os.path.join(local_path, 'website')):
            command = 'cp {0} {1}'.format(
                os.path.join(local_path, 'website', 'project', 'sample_local_settings.py'),
                os.path.join(local_path, 'website', 'project', 'local_settings.py')
            )
            local(command)


    def run_migrations(self, local_path, virtualenv):

        virtualenv_bin = os.path.join(virtualenv, 'bin')

        with lcd(os.path.join(local_path, 'website')):
            command = '{0} manage.py migrate'.format(os.path.join(virtualenv_bin, 'python'))
            local(command)


    def install_npm_packages(self, local_path):

        with lcd(local_path):
            command = 'npm install'
            local(command)


    def run_tmuxp(self, local_path):

        command = 'tmuxp load {0}'.format(os.path.join(local_path, '.tmuxp.yaml'))
        local(command)














