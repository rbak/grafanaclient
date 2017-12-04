from twcmanage.lib.grafanaclient.utils import base


class Dashboard(base.Resource):
    def __repr__(self):
        return '<Dashboard: %s>' % getattr(self, 'title', 'unknown-title')

    def update(self, json):
        """Update dashboard."""
        return self.manager.update(self.id, json)

    def delete(self):
        """Delete dashboard."""
        return self.manager.delete(self.uri)


class DashboardJson(base.JsonResource):
    def __init__(self, manager, info):
        super(DashboardJson, self).__init__(manager, info)
        self.title = info['dashboard']['title']

    def __repr__(self):
        return '<Dashboard: %s>' % getattr(self, 'title', 'unknown-title')

    def update(self, json):
        """Update dashboard."""
        return self.manager.update(self.id, json)

    def delete(self):
        """Delete dashboard."""
        return self.manager.delete(self.id)


class Tag(base.Resource):
    def __repr__(self):
        return '<Tag: %s>' % getattr(self, 'term', 'unknown-term')


class DashboardManager(base.BaseManager):
    resource_class = Dashboard

    def get(self, uri):
        """Get dashboard."""
        return self._get('/api/dashboards/%s' % uri, obj_class=DashboardJson)

    def list(self):
        """List dashboards."""
        return self._list('/api/search')

    def search(self, **kwargs):
        """Search dashboards."""
        url = '/api/search?'
        for arg in kwargs:
            url += '%s=%s&' % (arg, kwargs[arg])
        url = url[:-1]

        return self._list(url)

    def create(self, dashboard):
        """Create dashboard."""
        dashboard['id'] = None
        json = {'dashboard': dashboard}
        return self._post('/api/dashboards/db', json=json)

    def update(self, id, dashboard):
        """Update dashboard."""
        dashboard['id'] = id
        json = {'dashboard': dashboard, 'overwrite': True}
        return self._post('/api/dashboards/db', json=json)

    def _import(self, dashboard):
        """Import dashboard."""
        dashboard['id'] = None
        json = {'dashboard': dashboard, 'overwrite': True}
        return self._post('/api/dashboards/import', json=json)

    def delete(self, uri):
        """Delete dashboard."""
        return self._delete('/api/dashboards/%s' % uri)

    def get_home(self):
        return self._get('/api/dashboards/home')

    def list_tags(self):
        return self._list('/api/dashboards/tags', obj_class=Tag)
