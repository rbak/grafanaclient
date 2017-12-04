import urllib
from twcmanage.lib.grafanaclient.utils import base


class Renderer(base.FileManager):
    def render(self, slug, from_time, to_time, panel, **kwargs):
        """Render panel image."""
        path = "/render/dashboard-solo/db/%s?" % slug
        params = {'to': to_time, 'from': from_time, 'panelId': panel}
        for key in kwargs:
            params[key] = kwargs[key]
        path += urllib.urlencode(params)
        return self._get(path)
