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

        self.dokku_targets = self.get_dokku_targets()
        self.dokku_host = self.get_dokku_host()

        self.app_name = '-'.join(reversed(self.key.split('.')))

        self.check_dokku_server()
        self.check_remotes()


    def get_dokku_host(self):

        deployment = self.project_settings.get('deployment')
        try:
            return deployment.split('@')[1]
        except:
            raise Exception('unable to get dokku host')


    def get_dokku_targets(self):

        targets = self.project_settings.get('targets')

        try:
            return [i.strip() for i in targets.split(',')]
        except:
            return ['production', 'staging']



    def check_dokku_server(self):

        print((cyan(':' * 72)))
        print((cyan('checking dokku connection & account: {}'.format(self.dokku_host))))

        with lcd(self.project_dir):
            command = 'ssh dokku@{0} apps'.format(self.dokku_host)
            out = local(command, capture=True)

            print((cyan(out)))

            wanted_apps = {}
            have_apps = {}

            for t in self.dokku_targets:
                if t == 'production':
                    key = '{0}'.format(self.app_name)
                else:
                    key = '{0}-{1}'.format(self.app_name, t)

                wanted_apps[t] = key
                have_apps[t] = False

            for l in out.split('\n'):
                for k, v in wanted_apps.iteritems():
                    if l == v:
                        have_apps[k] = True

            for k, v in have_apps.iteritems():
                if not v:
                    print((yellow('app not installed: {}'.format(wanted_apps[k]))))
                    if prompt('Create it? Y/n', default='y').lower() == 'y':
                        self.create_app(wanted_apps[k])


    def create_app(self, app_name):

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

        wanted_remotes = {}
        have_remotes = {}

        for t in self.dokku_targets:
            if t == 'production':
                key = 'dokku@{0}:{1}'.format(self.dokku_host, self.app_name)
            else:
                key = 'dokku@{0}:{1}-{2}'.format(self.dokku_host, self.app_name, t)

            wanted_remotes[t] = key
            have_remotes[t] = False

        with lcd(self.project_dir):
            command = 'git remote -v'
            with quiet():
                out = local(command, capture=True)
                print((cyan(out)))

            for l in out.split('\n'):
                if l.startswith('dokku'):

                    _l = 'dokku' + l.split('\tdokku')[1].replace('(fetch)', '').replace('(push)', '').strip()

                    print(blue(_l))

                    for k, v in wanted_remotes.iteritems():
                        if _l == v:
                            have_remotes[k] = True

            for k, v in have_remotes.iteritems():
                if not v:
                    print((yellow('app "{}" not in remotes: {}'.format(k, wanted_remotes[k]))))
                    if prompt('add it? Y/n', default='y').lower() == 'y':
                        pass

                        if k == 'production':
                            _k = 'dokku'
                        else:
                            _k = 'dokku-{}'.format(k)

                        print(red(_k))

                        command = 'git remote rm {}'.format(_k)
                        with quiet():
                            local(command)


                        command = 'git remote add {0} {1}'.format(_k, wanted_remotes[k])
                        local(command)



    def run(self, no_input=False):

        if len(self.dokku_targets) == 1:
            command = 'git push -f dokku-{branch} {branch}:master'.format(branch=self.dokku_targets[0])
            local(command)

        else:
            branch = prompt('What branch to deploy {}?'.format('/'.join(self.dokku_targets)), default=self.dokku_targets[0]).lower()

            if branch == 'production':
                command = 'git push --force dokku master'
            else:
                command = 'git push --force dokku-{branch} {branch}:master'.format(branch=branch)

            local(command)

        # if branch == 's':
        #     command = 'git push -f dokku-staging staging:master'
        #     local(command)
        #
        # if branch == 'p':
        #     command = 'git push -f dokku master'
        #     local(command)
