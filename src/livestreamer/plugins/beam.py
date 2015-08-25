import re

from livestreamer.plugin import Plugin
from livestreamer.plugin.api import http, validate
from livestreamer.stream import LightStream

_url_re = re.compile("http(s)?://(\w+.)?beam.pro/(?P<channel>[^/]+)")

CHANNEL_INFO = "https://beam.pro/api/v1/channels/{0}"
CHANNEL_MANIFEST = "https://beam.pro/api/v1/channels/{0}/manifest.light"


class Beam(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")
        res = http.get(CHANNEL_INFO.format(channel))
        channel_info = http.json(res)

        if not channel_info["online"]:
            return

        res = http.get(CHANNEL_MANIFEST.format(channel_info["id"]))
        assets = http.json(res)
        streams = {}
        for video in assets["resolutions"]:
            name = "{0}p".format(video["height"])
            stream = LightStream(self.session, video["url"])
            streams[name] = stream

        return streams

__plugin__ = Beam
