import websocket
import json

from .stream import Stream
from .wrappers import StreamIOIterWrapper
from ..exceptions import StreamError


class LightStream(Stream):
    """A Light stream using the websocket library.

    *Attributes:*

    - :attr:`url`  The websocket URL to the stream.

    """

    __shortname__ = "light"

    def __init__(self, session, url):
        Stream.__init__(self, session)

        self.logger = session.logger.new_module("stream.light")
        self.url = url

    def __repr__(self):
        return "<LightStream({0!r})>".format(self.url)

    def open(self):
        timeout = self.session.options.get("http-timeout")

        try:
            self.logger.debug("Creating websocket connection... Timeout: {}".format(timeout))
            ws = websocket.create_connection(self.url, timeout)
            self.logger.debug("Getting 'State' Frame...")
            first_frame = ws.recv()
            first_frame_data = json.loads(first_frame.replace(b"\x00", b"").decode("utf-8"))
            self.logger.debug("State: '{}'".format(first_frame_data['State']))

            # Check if state is a known one that works (i.e. stream will start)
            if first_frame_data['State'] in ['READ_BODY', 'ACTIVE', 'IDLE']:
                self.logger.debug("This looks ok I guess... Go!")
            else:
                self.logger.error("Invalid State: '{}'".format(first_frame_data['State']))
                raise StreamError
        except websocket.WebSocketException as e:
            self.logger.error("WebSocketException: '{}'".format(e))
            raise StreamError

        self.logger.debug("Starting streaming using websockets...")

        fd = StreamIOIterWrapper(ws)

        return fd

