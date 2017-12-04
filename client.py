from twcmanage.lib.grafanaclient.utils import http
import organizations
import users
import dashboards
import datasources
import renderer
import time


class Client(object):

    """Client for the Grafana v2 API.

    :param string endpoint: A user-supplied endpoint URL for the monasca api
                            service.
    :param string token: Api Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new http client for the grafana API."""
        self.http_client = http.HTTPClient(*args, **kwargs)
        self.http_client.login()
        self.orgs = organizations.OrganizationManager(self.http_client)
        self.users = users.UserManager(self.http_client)
        self.dashboards = dashboards.DashboardManager(self.http_client)
        self.datasources = datasources.DatasourceManager(self.http_client)
        self.renderer = renderer.Renderer(self.http_client)

    def get_org(self):
        return self.orgs.get()

    def switch_org(self, orgname=None, orgid=None):
        if orgname:
            orgs = self.orgs.list()
            for org in orgs:
                if org.name == orgname:
                    orgid = org.id
        return self.users.orgs.switch_current(orgid)

    def render(self, slug, panel=1, from_time=None, to_time=None, timeout=None, output=None):
        if not to_time:
            to_time = time.time()
        if not from_time:
            from_time = to_time - 6 * 60 * 60
        response = self.renderer.render(slug, int(from_time * 1000), int(to_time * 1000), panel,
                                        timeout=60)
        if not output:
            output = "%s-%s.png" % (slug, panel)
        data = bytearray(response.content)
        with open(output, 'w') as f:
            f.write(data)
