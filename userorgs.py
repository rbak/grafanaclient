from twcmanage.lib.grafanaclient.utils import base


class UserOrg(base.Resource):
    def __repr__(self):
        return '<User-Org: %s>' % getattr(self, 'name', 'unknown-name')


class UserOrgManager(base.BaseManager):
    resource_class = UserOrg

    def list(self, userid=None):
        """List orgs for user."""
        if userid:
            return self._list("/api/users/%s/orgs" % userid)
        else:
            return self._list("/api/user/orgs")

    def switch_current(self, orgid):
        """Switch active org. Current user only."""
        return self._post("/api/user/using/%s" % orgid)
