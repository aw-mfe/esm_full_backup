# -*- coding: utf-8 -*-

import base64
import json
import os
import re
import requests
import sys
import urllib.parse as urlparse
from configparser import ConfigParser, NoSectionError
requests.packages.urllib3.disable_warnings()

    
class Config(object):
    """
    Find the config settings which include:

     - esmhost
     - esmuser
     - esmpass
    """
    CONFIG = None

    @classmethod
    def find_ini(cls):
        """
        Attempt to locate a mfe_saw.ini file
        """
        config = ConfigParser()
        module_dir = os.path.dirname(sys.modules[__name__].__file__)

        if 'APPDATA' in os.environ:
            conf_path = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:
            conf_path = os.environ['XDG_CONFIG_HOME']
        elif 'HOME' in os.environ:
            conf_path = os.path.join(os.environ['HOME'])
        else:
            conf_path = None

        paths = [os.path.join(module_dir, '.mfe_saw.ini'), '.mfe_saw.ini']
        if conf_path is not None:
            paths.insert(1, os.path.join(conf_path, '.mfe_saw.ini'))
        config.read(paths)
        cls.CONFIG = config

    def __init__(self, **kwargs):
        """
        Initialize a Config instance.

        """
        self._kwargs = kwargs
        self.find_ini()
        self._find_envs()
        self._init_config()

    def _find_envs(self):
        """
        Builds a dict with env variables set starting with 'ESM'.
        """
        self._envs = {self._kenv: self._venv
                      for self._kenv, self._venv in os.environ.items()
                      if self._kenv.startswith('ESM')}

    def _init_config(self):
        """
        """
        if not self.CONFIG:
            raise FileNotFoundError('mfe_ini file not found.')

        try:
            self.types = dict(self.CONFIG.items('types'))
        except NoSectionError:
            self.types = None

        try:
            self.recs = dict(self.CONFIG.items('recs'))
        except NoSectionError:
            self.recs = None

        try:
            self._ini = dict(self.CONFIG.items('esm'))
            self.__dict__.update(self._ini)
        except NoSectionError:
            print("Section [esm] not found in mfe_saw.ini")

        # any envs overwrite the ini values
        if self._envs:
            self._envs = {self._key.lower(): self._val
                          for self._key, self._val in self._envs.items()}
        self.__dict__.update(self._envs)


class ESM(object):
    """
    """

    def __init__(self, hostname, username, password):
        """
        """
        self._host = hostname
        self._user = username
        self._passwd = password

        self._base_url = 'https://{}/rs/esm/'.format(self._host)
        self._int_url = 'https://{}/ess'.format(self._host)

        self._v9_creds = '{}:{}'.format(self._user, self._passwd)
        self._v9_b64_creds = base64.b64encode(self._v9_creds.encode('utf-8'))

        self._v10_b64_user = base64.b64encode(self._user.encode('utf-8')).decode()
        self._v10_b64_passwd = base64.b64encode(self._passwd.encode('utf-8')).decode()
        self._v10_params = {"username": self._v10_b64_user,
                            "password": self._v10_b64_passwd,
                            "locale": "en_US",
                            "os": "Win32"}
        self._headers = {'Content-Type': 'application/json'}

    def login(self):
        """
        Log into the ESM
        """
        self._headers = {'Authorization': 'Basic ' +
                         self._v9_b64_creds.decode('utf-8'),
                         'Content-Type': 'application/json'}
        self._method = 'login'
        self._data = self._v10_params
        self._resp = self.post(self._method, data=self._data,
                               headers=self._headers, raw=True)

        if self._resp.status_code in [400, 401]:
            print('Invalid username or password for the ESM')
            sys.exit(1)
        elif 402 <= self._resp.status_code <= 600:
            print('ESM Login Error:', self._resp.text)
            sys.exit(1)

        self._data = ''
        self._headers = {'Content-Type': 'application/json'}
        self._headers['Cookie'] = self._resp.headers.get('Set-Cookie')
        self._headers['X-Xsrf-Token'] = self._resp.headers.get('Xsrf-Token')
        self._headers['SID'] = self._resp.headers.get('Location')

    def start_full_backup(self):
        """
        """
        self._method = 'ESSMGT_DBBACKUPFULL'
        if self._headers.get('SID') is not None:
            self._session = {'SID': self._headers['SID']}
            self._data = self._session
        else:
            self._data = {}

        self._resp = self.post(self._method,
                               data=self._data,
                               headers=self._headers)
        return self._resp

    def post(self, method, data=None, callback=None, raw=None,
             headers=None, verify=False):
        """
        """
        self._method = method
        self._data = data
        self._callback = callback
        self._headers = headers
        self._raw = raw
        self._verify = verify

        if not self._method:
            raise ValueError("Method must not be None")

        self._url = self._base_url + self._method
        if self._method == self._method.upper():
            self._url = self._int_url
            self._data = self._format_params(self._method, **self._data)
        else:
            self._url = self._base_url + self._method
            if self._data:
                self._data = json.dumps(self._data)

        self._resp = self._post(self._url, data=self._data,
                                headers=self._headers, verify=self._verify)

        if self._raw:
            return self._resp

        if 200 <= self._resp.status_code <= 300:
            try:
                self._resp = self._resp.json()
                self._resp = self._resp.get('return')
            except json.decoder.JSONDecodeError:
                self._resp = self._resp.text
            if self._method == self._method.upper():
                self._resp = self._format_resp(self._resp)
            if self._callback:
                self._resp = self._callback(self._resp)
            return self._resp
        if 400 <= self._resp.status_code <= 600:
            print('ESM Error:', self._resp.text)
            sys.exit(1)



    @staticmethod
    def _post(url, data=None, headers=None, verify=False):
        """
        Method that actually kicks off the HTTP client.

        Args:
            url (str): URL to send the post to.
            data (str): Any payload data for the post.
            headers (str): http headers that hold cookie data after
                            authentication.
            verify (bool): SSL cerificate verification

        Returns:
            Requests Response object
        """
        try:
            return requests.post(url, data=data, headers=headers,
                                 verify=verify)

        except requests.exceptions.ConnectionError:
            print("Unable to connect to ESM: {}".format(url))
            sys.exit(1)

    @staticmethod
    def _format_params(cmd, **params):
        """
        Format API call
        """

        params = {key: val
                  for key, val in params.items() if val is not None}

        params = '%14'.join([key + '%13' + val + '%13'
                             for (key, val) in params.items()])
        if params:
            params = 'Request=API%13' + cmd + '%13%14' + params + '%14'
        else:
            params = 'Request=API%13' + cmd + '%13%14'
        return params

    @staticmethod
    def _format_resp(resp):
        """
        Format API response
        """
        resp = re.search('Response=(.*)', resp).group(1)
        resp = resp.replace('%14', ' ')
        pairs = resp.split()
        formatted = {}
        for pair in pairs:
            pair = pair.replace('%13', ' ')
            pair = pair.split()
            key = pair[0]
            if key == 'ITEMS':
                value = dehexify(pair[-1])
            else:
                value = urlparse.unquote(pair[-1])
            formatted[key] = value
        return formatted


def dehexify(data):
    """
    Decode hex/url data
    """

    hexen = {
        '\x1c': ',',  # Replacing Device Control 1 with a comma.
        '\x11': ',',  # Replacing Device Control 2 with a new line.
        '\x12': '\n',  # Space
        '\x22': '"',  # Double Quotes
        '\x23': '#',  # Number Symbol
        '\x27': '\'',  # Single Quote
        '\x28': '(',  # Open Parenthesis
        '\x29': ')',  # Close Parenthesis
        '\x2b': '+',  # Plus Symbol
        '\x2d': '-',  # Hyphen Symbol
        '\x2e': '.',  # Period, dot, or full stop.
        '\x2f': '/',  # Forward Slash or divide symbol.
        '\x7c': '|',  # Vertical bar or pipe.
    }

    uri = {
        '%11': ',',  # Replacing Device Control 1 with a comma.
        '%12': '\n',  # Replacing Device Control 2 with a new line.
        '%20': ' ',  # Space
        '%22': '"',  # Double Quotes
        '%23': '#',  # Number Symbol
        '%27': '\'',  # Single Quote
        '%28': '(',  # Open Parenthesis
        '%29': ')',  # Close Parenthesis
        '%2B': '+',  # Plus Symbol
        '%2D': '-',  # Hyphen Symbol
        '%2E': '.',  # Period, dot, or full stop.
        '%2F': '/',  # Forward Slash or divide symbol.
        '%3A': ':',  # Colon
        '%7C': '|',  # Vertical bar or pipe.
    }

    for (enc, dec) in hexen.items():
        data = data.replace(enc, dec)

    for (enc, dec) in uri.items():
        data = data.replace(enc, dec)

    return data
