pbi.io - Internal CLI Tool
==========================


Installation
------------

    pip install -e git+https://github.com/palmbeach-interactive/pbi-client.git#egg=pbi-client

Configuration
-------------

Create a config file at '~/.pbi.cfg' (this is the default path. can alternatively be provided using the '--config' option)

    nano ~/.pbi.cfg

should look like;

    api_url=https://service.pbi.io/
    workspace=~/code/
    virtualenv=~/srv/
    [user]
    email=karl.klammer@pbi.io
    api_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

You can find your API key on the service platform: https://service.pbi.io/accounts/profile/api-key/



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
