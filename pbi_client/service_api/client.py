import requests

HEADER = '\033[97m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


API_BASE_URL = 'https://service.hazelfire.com/'
API_CLIENT_HEADERS = {}


class APIException(Exception):
    pass


class APIClient(object):

    def __init__(self, email, api_key, api_base_url=None):

        if not email:
            raise IOError('email not configured')

        if not api_key:
            raise IOError('api_key not configured')

        self.client_headers = API_CLIENT_HEADERS
        self.client_headers['Authorization'] = 'ApiKey {}:{}'.format(email, api_key)
        self.api_base_url = api_base_url + 'api/v1/' if api_base_url else API_BASE_URL + 'api/v1/'

    def check_version(self):

        from .. import  __version__

        print __version__

        pass



class ApplicationAPIClient(APIClient):


    def get(self, url, *args, **kwargs):
        r = requests.get(url, headers=self.client_headers, *args, **kwargs)

        if not r.status_code == 200:
            raise APIException('status: {} accessing resource: {}'.format(r.status_code, url))

        return r

    def list(self):
        url = self.api_base_url + 'infrastructure/application/'
        r = self.get(url)
        return r.json()

    def detail(self, key):
        url = self.api_base_url + 'infrastructure/application/{}/'.format(key)
        r = self.get(url)
        return r.json()

    def get_deployer(self, key):

        url = self.api_base_url + 'infrastructure/application/{}/deploy/'.format(key)
        r = self.get(url)
        return r.json()

    def deploy_run(self, deployer):

        url = self.api_base_url + 'infrastructure/runner/{}/run/'.format(deployer['uuid'])
        r = requests.get(url, headers=self.client_headers, stream=True)
        for line in r.iter_lines():
            if line:
                print(colorize(line))




def colorize(line):

    color = HEADER

    if line.startswith('TASK'):
        color = BOLD

    if line.startswith('ok'):
        color = OKGREEN

    if line.startswith('changed'):
        color = WARNING

    if line.startswith('skipping'):
        color = OKBLUE

    if line.startswith('task path'):
        color = UNDERLINE

    return color + line + ENDC