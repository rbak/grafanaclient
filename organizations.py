from twcmanage.lib.grafanaclient.utils import base
import orgusers


class Organization(base.Resource):
    def __repr__(self):
        return '<Organization: %s>' % getattr(self, 'name', 'unknown-name')

    def update(self, name=None, address=None):
        return self.manager.update(orgid=self.id, name=name, address=address)

    def list_users(self):
        return self.manager.users.list(orgid=self.id)

    def add_user(self, role, login):
        return self.manager.users.add(role=role, login=login, orgid=self.id)

    def update_user(self, role, userid):
        return self.manager.users.update(role=role, userid=userid, orgid=self.id)

    def remove_user(self, userid):
        return self.manager.users.remove(userid=userid, orgid=self.id)

    def delete(self):
        return self.manager.delete(self.id)


class OrganizationManager(base.BaseManager):
    resource_class = Organization

    def __init__(self, client):
        super(OrganizationManager, self).__init__(client)
        self.users = orgusers.OrgUserManager(client)

    def get(self, orgid=None):
        """Get org."""
        if orgid:
            return self._get('/api/orgs/%s' % orgid)
        else:
            return self._get('/api/org')

    def list(self):
        """List all orgs."""
        return self._list('/api/orgs')

    def create(self, name, address=None):
        """Create org."""
        data = {
            "name": name
        }
        return self._post('/api/orgs', json=data)

    def update(self, orgid=None, name=None, address=None):
        """Update org."""
        data = {}
        if name:
            data['name'] = name
        if address:
            data['address'] = address

        if orgid:
            return self._put('/api/orgs/%s' % orgid, json=data)
        else:
            return self._put('/api/org', json=data)

    def delete(self, orgid):
        """Delete org. Admin Only"""
        return self._delete('/api/orgs/%s' % orgid)
