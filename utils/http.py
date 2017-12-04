# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Time Warner Cable
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
import requests
import socket

from requests.auth import HTTPBasicAuth


def get_system_ca_file():
    """Return path to system default CA file."""
    # Standard CA file locations for Debian/Ubuntu, RedHat/Fedora,
    # Suse, FreeBSD/OpenBSD, MacOSX, and the bundled ca
    ca_path = ['/etc/ssl/certs/ca-certificates.crt',
               '/etc/pki/tls/certs/ca-bundle.crt',
               '/etc/ssl/ca-bundle.pem',
               '/etc/ssl/cert.pem',
               '/System/Library/OpenSSL/certs/cacert.pem',
               requests.certs.where()]
    for ca in ca_path:
        if os.path.exists(ca):
            return ca


class HTTPClient(object):
    def __init__(self, endpoint, write_timeout=None, read_timeout=None, **kwargs):
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        self.endpoint = endpoint
        self.write_timeout = write_timeout
        self.read_timeout = read_timeout

        self.api_token = kwargs.get('token')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.cookie = None

        self.cert_file = kwargs.get('cert_file')
        self.key_file = kwargs.get('key_file')

        self.ssl_connection_params = {
            'os_cacert': kwargs.get('os_cacert'),
            'cert_file': kwargs.get('cert_file'),
            'key_file': kwargs.get('key_file'),
            'insecure': kwargs.get('insecure'),
        }

        self.verify_cert = None
        if endpoint.split(':')[0] == "https":
            if kwargs.get('insecure'):
                self.verify_cert = False
            else:
                self.verify_cert = kwargs.get(
                    'os_cacert', get_system_ca_file())

    def _http_request(self, url, method, **kwargs):
        """Send an http request with the specified characteristics.

        Wrapper around requests.request to handle tasks such as
        setting headers and error handling.
        """

        auth = None
        if self.api_token:
            kwargs['headers'].setdefault('Authorization', 'Bearer ' + self.api_token)
        elif 'login' in kwargs:
            del kwargs['login']
        elif not self.cookie:
            auth = HTTPBasicAuth(self.username, self.password)

        if self.cert_file and self.key_file:
            kwargs['cert'] = (self.cert_file, self.key_file)

        if self.verify_cert is not None:
            kwargs['verify'] = self.verify_cert

        timeout = None
        if method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            timeout = self.write_timeout
        elif method is 'GET':
            timeout = self.read_timeout

        try:
            resp = requests.request(
                method,
                self.endpoint + url,
                timeout=timeout,
                auth=auth,
                cookies=self.cookie,
                **kwargs)
        except socket.gaierror as e:
            message = ("Error finding address for %(url)s: %(e)s" %
                       {'url': self.endpoint + url, 'e': e})
            raise Exception(message=message)
        except (socket.error, socket.timeout) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s" %
                       {'endpoint': endpoint, 'e': e})
            raise Exception(message=message)
        except requests.Timeout as e:
            endpoint = self.endpoint
            message = ("Error %(method)s timeout request to %(endpoint)s %(e)s" %
                       {'method': method, 'endpoint': endpoint, 'e': e})
            raise Exception(message=message)

        if resp.status_code != 200:
            e = {}
            if resp.content:
                try:
                    e = json.loads(resp.content)
                except:
                    e['message'] = resp.content
            e['status_code'] = resp.status_code
            raise Exception(e)

        return resp

    def json_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')
        kwargs['headers'].setdefault('Accept', 'application/json')

        resp = self._http_request(url, method, **kwargs)
        body = resp.content
        if 'application/json' in resp.headers.get('content-type', ''):
                body = resp.json()
        else:
            body = None

        return resp, body

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')
        return self._http_request(url, method, **kwargs)

    def client_request(self, method, url, **kwargs):
        resp, body = self.json_request(method, url, **kwargs)
        return resp

    def head(self, url, **kwargs):
        return self.client_request("HEAD", url, **kwargs)

    def get(self, url, **kwargs):
        return self.client_request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.client_request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.client_request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.raw_request("DELETE", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.client_request("PATCH", url, **kwargs)

    def raw_get(self, url, **kwargs):
        return self.raw_request("GET", url, **kwargs)

    def login(self):
        json = {
            'user': self.username,
            'password': self.password,
            'email': "",
            'login': True,
        }
        data = self.post('/login', json=json, login=True)
        self.cookie = data.cookies
