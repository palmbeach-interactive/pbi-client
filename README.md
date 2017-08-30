pbi.io - Internal CLI Tool
==========================


Installation
------------

Make sure no virtualenv is activated. the pbi client should be installed globally.

    sudo pip install -I -e "git+https://github.com/palmbeach-interactive/pbi-client.git#egg=pbi-client"



Notes Python3
-------------


Before installing run:

    sudo pip uninstall Fabric


Configuration
-------------

Create a config file at '~/.pbi.cfg' (this is the default path. can alternatively be provided using the '--config' option)

    nano ~/.pbi.cfg

should look like;

    api_url=https://service.pbi.io/
    workspace=~/code/
    virtualenv=~/srv/
    infrastructure=~/code/infrastructure/
    [user]
    email=karl.klammer@pbi.io
    api_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

You can find your API key on the service platform: https://service.pbi.io/accounts/profile/api-key/



Infrastructure Repository
-------------------------

    sudo pip install ansible


Ansible settings

    nano ~/.ansible.cfg
    
Could look like:

    [defaults]
    hash_behaviour = merge
    host_key_checking = False
    roles_path = ~/ansible/roles
    retry_files_enabled = False
    
    
Eventually you have to create the *roles* directory:

    mkdir ~/ansible/roles


Infrastructure repository is expected to be in folder `~/code/infrastructure/` configured above.

    cd ~/code
    git clone <ask for repository> infrastructure
    cd infrastructure/ansible
    ansible-galaxy install -r requirements.yml


Verify Installation
-------------------

    pbi list



Usage
-----

    pbi list                                                                                                                                               │    pbi list
    pbi init                                                                                                                                               │    pbi list
    pbi info (example.com)                                                                                                                                         │    pbi info (example.com)
    pbi deploy (example.com)                                                                                                                                       │    pbi deploy (example.com)
    pbi incubate (example.com)                                                                                                                                     │    pbi incubate (example.com)
    pbi install (example.com)
