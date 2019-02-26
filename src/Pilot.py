import logging
import asyncio
import json
import websockets
from CvThread import CvThread


class Pilot(CvThread):

    def __init__(self, *args, **kwargs):
        super(Pilot, self).__init__(*args, **kwargs)

    def connect2car(self):
        # Create a new Async Loop for this thread (this is necessary to use websockets)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Connect to Car Controls
        logging.info("Waiting for controls...")
        while not self._evt.isSet():
            try:
                self._ws = asyncio.get_event_loop().run_until_complete(websockets.connect("ws://192.168.12.250:80/ws"))
                logging.info("Controls Connected.")
                break
            except OSError:
                logging.error("Connection to controls Failed. retrying...", exc_info=True)
            self._evt.wait(0.01)

    async def _wsRun(self, cmd):
        if self._ws is not None:
            await self._ws.send(json.dumps(cmd))
            logging.debug("> {}".format(json.dumps(cmd)))
            res = await self._ws.recv()
            self._wsLastCmd = cmd
            return res
        return -1

    def run(self):
        self._ws = None
        self.connect2car()
        super(Pilot, self).run()

    # Override this method
    def _drive(self, data):
        SPEED = 31 #28
        THRESHOLD = 15

        if data is None:
            # STOP
            asyncio.get_event_loop().run_until_complete(self._wsRun({"cmd": "run", "args": [4, 0, 0]}))
            return 0

        xdiff = int(data[0])
        steering = abs(int(data[0])) * 0.4

        if (steering > 100):
            steering = 100

        if xdiff > THRESHOLD:    # Left
            steering *= 1

        elif xdiff < -THRESHOLD:  # Right
            steering *= -1

        else:            # Forward
            steering *= 0
        print([2, SPEED, steering])

        asyncio.get_event_loop().run_until_complete(self._wsRun({"cmd": "run", "args": [2, SPEED, steering]}))
