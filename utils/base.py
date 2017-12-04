# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
# Copyright 2012 Grid Dynamics
# Copyright 2013 OpenStack Foundation
# (C) Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Time Warner Cable
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Base utilities to build API operation managers and objects on top of.
"""

# E1102: %s is not callable
# pylint: disable=E1102

import copy
import six


class BaseManager(object):
    """Basic manager type providing common operations.

    Managers interact with a particular type of API (dashboards, organizations,
    etc.) and provide CRUD operations for them.
    """
    resource_class = None

    def __init__(self, client):
        """Initializes BaseManager with `client`.

        :param client: instance of BaseClient descendant for HTTP requests
        """
        super(BaseManager, self).__init__()
        self.client = client

    def _list(self, url, obj_class=None, json=None):
        """List the collection.

        :param url: a partial URL, e.g., '/dashboards'
        :param obj_class: class for constructing the returned objects
            (self.resource_class will be used by default)
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        """
        if json:
            body = self.client.post(url, json=json).json()
        else:
            body = self.client.get(url).json()

        if obj_class is None:
            obj_class = self.resource_class

        return [obj_class(self, res) for res in body if res]

    def _get(self, url, obj_class=None):
        """Get an object from collection.

        :param url: a partial URL, e.g., '/dashboards'
        :param obj_class: class for constructing the returned objects
            (self.resource_class will be used by default)
        """
        body = self.client.get(url).json()
        if obj_class is None:
            obj_class = self.resource_class
        return obj_class(self, body)

    def _post(self, url, json=None, return_raw=True):
        """Create an object.

        :param url: a partial URL, e.g., '/dashboards'
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param return_raw: flag to force returning raw JSON instead of
            Python object of self.resource_class
        """
        if json:
            body = self.client.post(url, json=json).json()
        else:
            body = self.client.post(url).json()
        if return_raw:
            return body
        return self.resource_class(self, body)

    def _put(self, url, json=None, return_raw=True):
        """Update an object with PUT method.

        :param url: a partial URL, e.g., '/dashboards'
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param return_raw: flag to force returning raw JSON instead of
            Python object of self.resource_class
        """
        resp = self.client.put(url, json=json)
        # PUT requests may not return a body
        if resp.content:
            body = resp.json()
            if return_raw:
                return body
            return self.resource_class(self, body)

    def _patch(self, url, json=None, return_raw=True):
        """Update an object with PATCH method.

        :param url: a partial URL, e.g., '/servers'
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param return_raw: flag to force returning raw JSON instead of
            Python object of self.resource_class
        """
        body = self.client.patch(url, json=json).json()
        if return_raw:
            return body
        return self.resource_class(self, body)

    def _delete(self, url):
        """Delete an object.

        :param url: a partial URL, e.g., '/dashboards/my-server'
        """
        return self.client.delete(url)


class FileManager(object):
    """File manager type providing file specific operations.."""

    def __init__(self, client):
        """Initializes FileManager with `client`.

        :param client: instance of BaseClient descendant for HTTP requests
        """
        super(FileManager, self).__init__()
        self.client = client

    def _get(self, url):
        """Get a file.

        :param url: a partial URL, e.g., '/dashboards'
        """
        body = self.client.raw_get(url)
        return body


class Resource(object):
    """Base class for resources."""

    def __init__(self, manager, info):
        """Populate and bind to a manager.

        :param manager: BaseManager object
        :param info: dictionary representing resource attributes
        """
        self.manager = manager
        self._info = info
        self._add_details(info)

    def __repr__(self):
        reprkeys = sorted(k
                          for k in self.__dict__.keys()
                          if k[0] != '_' and k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id == other.id
        return self._info == other._info

    def to_dict(self):
        return copy.deepcopy(self._info)


class JsonResource(object):
    """Base class for json resources."""

    def __init__(self, manager, info):
        """Populate and bind to a manager.

        :param manager: BaseManager object
        :param info: json representation of resource
        """
        self.manager = manager
        self._json = info

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._json == other._json
