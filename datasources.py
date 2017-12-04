from twcmanage.lib.grafanaclient.utils import base


class Datasource(base.Resource):
    def __repr__(self):
        return '<Datasource: %s>' % getattr(self, 'name', 'unknown-name')

    def update(self, json):
        """Update datasource."""
        return self.manager.update(self.id, json)

    def delete(self):
        """Delete datasource."""
        return self.manager.delete(self.id)


class DatasourceManager(base.BaseManager):
    resource_class = Datasource

    def list(self):
        """List datasources."""
        return self._list('/api/datasources')

    def get(self, id):
        """Get datasource."""
        return self._get('/api/datasources/%s' % id)

    def create(self, json):
        """Create datasource."""
        return self._post('/api/datasources', json=json)

    def update(self, id, json):
        """Update datasource."""
        return self._put('/api/datasources/%s' % id, json=json)

    def delete(self, id):
        """Delete datasource."""
        return self._delete('/api/datasources/%s' % id)
