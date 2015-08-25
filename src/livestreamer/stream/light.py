import websocket

from .stream import Stream
from .wrappers import StreamIOIterWrapper
from ..exceptions import StreamError


class LightStream(Stream):
    """A Light stream using the websocket library.

    *Attributes:*

    - :attr:`url`  The websocket URL to the stream.

    """

    __shortname__ = "light"

    # {"State":"ACTIVE"} with 0x00 inbetween for some reason...
    handshake_ok = b'{\x00"\x00S\x00t\x00a\x00t\x00e\x00"\x00:\x00"\x00A\x00C\x00T\x00I\x00V\x00E\x00"\x00}\x00'

    def __init__(self, session_, url):
        Stream.__init__(self, session_)

        self.url = url

    def __repr__(self):
        return "<LightStream({0!r})>".format(self.url)

    def open(self):
        timeout = self.session.options.get("http-timeout")  # we use this for the time being

        try:
            ws = websocket.create_connection(self.url, timeout)
            first_frame = ws.recv()
            if first_frame != self.handshake_ok:
                raise StreamError
        except websocket.WebSocketException:
            raise StreamError

        fd = StreamIOIterWrapper(ws)

        return fd

