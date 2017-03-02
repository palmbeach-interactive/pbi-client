# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import sys
import shutil
from fabric.api import local, lcd, warn_only, env, warn_only, quiet
from fabric.colors import green, red, blue, yellow, cyan
from fabric.operations import prompt

env.warn_only = True

class DokkuDeployer(object):

    def __init__(self, key, project_dir, project_settings):
        self.key = key
        self.project_dir = project_dir
        self.project_settings = project_settings

        self.dokku_host = self.get_dokku_host()

        # get host


        self.app_name = '-'.join(reversed(self.key.split('.')))

        self.check_dokku_server()
        self.check_remotes()


    def get_dokku_host(self):

        deployment = self.project_settings.get('deployment')
        try:
            return deployment.split('@')[1]
        except:
            raise Exception('unable to get dokku host')



    def check_dokku_server(self):

        print((cyan(':' * 72)))
        print((cyan('checking dokku connection & account: {}'.format(self.dokku_host))))

        with lcd(self.project_dir):
            command = 'ssh dokku@{0} apps'.format(self.dokku_host)
            out = local(command, capture=True)

            print((cyan(out)))

            wanted_apps = {
                'production': '{0}'.format(self.app_name),
                'staging': '{0}-staging'.format(self.app_name)
            }
            have_apps = {
                'production': False,
                'staging': False
            }

            for l in out.split('\n'):
                if l == wanted_apps['production']:
                    have_apps['production'] = True
                if l == wanted_apps['staging']:
                    have_apps['staging'] = True

        if not (have_apps['production'] and have_apps['staging']):

            if prompt('Apps do not exist. Create them? Y/n', default='y').lower() == 'y':
                self.create_app('production')
                self.create_app('staging')


    def create_app(self, type):

        if type == 'production':
            app_name = '{0}'.format(self.app_name)
        if type == 'staging':
            app_name = '{0}-staging'.format(self.app_name)

        print((cyan('app:create: {0}'.format(app_name))))

        command = 'ssh dokku@{0} apps:create {1}'.format(self.dokku_host, app_name)
        local(command)

        if prompt('Add postgres database? Y/n', default='y').lower() == 'y':
            command = 'ssh dokku@{0} postgres:create {1}'.format(self.dokku_host, app_name)
            local(command)
            command = 'ssh dokku@{0} postgres:link {1} {2}'.format(self.dokku_host, app_name, app_name)
            local(command)


        if prompt('Add redis? Y/n', default='y').lower() == 'y':
            command = 'ssh dokku@{0} redis:create {1}'.format(self.dokku_host, app_name)
            local(command)
            command = 'ssh dokku@{0} redis:link {1} {2}'.format(self.dokku_host, app_name, app_name)
            local(command)




    def check_remotes(self):


        wanted_remotes = {
            'production': 'dokku@{0}:{1}'.format(self.dokku_host, self.app_name),
            'staging': 'dokku@{0}:{1}-staging'.format(self.dokku_host, self.app_name)
        }
        have_remotes = {
            'production': False,
            'staging': False
        }
        add_remotes = {
            'production': False,
            'staging': False
        }

        with lcd(self.project_dir):
            command = 'git remote -v'
            with quiet():
                out = local(command, capture=True)
                print((cyan(out)))

            for l in out.split('\n'):

                if l.startswith('dokku') and not have_remotes['production'] and not 'staging' in l:
                    have_remotes['production'] = wanted_remotes['production'] in l

                if l.startswith('dokku-staging') and not have_remotes['staging']:
                    have_remotes['staging'] = wanted_remotes['staging'] in l

        if not have_remotes['production']:
            add_remotes['production'] = prompt('Production repository does not in remotes. Add it? Y/n', default='y').lower() == 'y'

        if not have_remotes['staging']:
            add_remotes['staging'] = prompt('Staging repository does not in remotes. Add it? Y/n', default='y').lower() == 'y'


        if add_remotes['production'] or add_remotes['staging']:

            with lcd(self.project_dir):

                if add_remotes['production']:
                    command = 'git remote rm dokku'
                    with quiet():
                        local(command)
                    command = 'git remote add dokku {0}'.format(wanted_remotes['production'])
                    local(command)

                if add_remotes['staging']:
                    command = 'git remote rm dokku-staging'
                    with quiet():
                        local(command)
                    command = 'git remote add dokku-staging {0}'.format(wanted_remotes['staging'])
                    local(command)




    def run(self, no_input=False):

        branch = prompt('What branch to deploy staging/production? S/p', default='s').lower()

        if branch == 's':
            command = 'git push -f dokku-staging staging:master'
            local(command)

        if branch == 'p':
            command = 'git push -f dokku master'
            local(command)
