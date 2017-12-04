from twcmanage.lib.grafanaclient.utils import base


class OrgUser(base.Resource):
    def __repr__(self):
        return '<Org-User: %s>' % getattr(self, 'login', 'unknown-login')

    def update(self, role):
        return self.manager.update(role, self.userId, orgid=self.orgId)

    def remove(self):
        return self.manager.remove(self.userId, orgid=self.orgId)


class OrgUserManager(base.BaseManager):
    resource_class = OrgUser

    def list(self, orgid=None):
        """List users in org."""
        if orgid:
            return self._list("/api/orgs/%s/users" % orgid)
        else:
            return self._list("/api/org/users")

    def add(self, role, login, orgid=None):
        """Add a user to the org."""
        data = {
            "role": role,
            "loginOrEmail": login
        }
        if orgid:
            return self._post("/api/orgs/%s/users" % orgid, json=data)
        else:
            return self._post("/api/org/users", json=data)

    def update(self, role, userid, orgid=None):
        """Update a users role within the org."""
        data = {
            "role": role,
        }
        if orgid:
            return self._patch("/api/orgs/%s/users/%s" % (orgid, userid),
                               json=data)
        else:
            return self._patch("/api/org/users/%s" % userid, json=data)

    def remove(self, userid, orgid=None):
        """Remove user from the org."""
        if orgid:
            return self._delete("/api/orgs/%s/users/%s" % (orgid, userid))
        else:
            return self._delete("/api/org/users/%s" % userid)
