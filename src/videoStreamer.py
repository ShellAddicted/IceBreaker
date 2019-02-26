import time
import logging
import io
import queue

try:
    import tornado
    import tornado.web
    import tornado.websocket
except ImportError:
    raise ImportError("Install tornado, example: #pip3 install tornado")

try:
    import picamera
except ImportError:
    raise ImportError("Install picamera, example: #pip3 install picamera")

frames = queue.LifoQueue(1)

class StreamingOutput(object):

    def __init__(self, showFPS=False):
        self._showFPS = showFPS
        self._buffer = io.BytesIO()

        # FPS
        self._count = 0
        self._stx = time.time()
        self.FPS = -1

    def _detectFPS(self):
        self._count += 1
        if self._count == 60:
            self.FPS = self._count / (time.time() - self._stx)
            logging.info("FPS: {}".format(self.FPS))
            # Reset counters
            self.count = 0
            self.stx = time.time()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):  # New Frame available
            if self._showFPS:
                self._detectFPS()
            self._buffer.truncate()
            frames.put(self._buffer.getvalue())
            self._buffer.seek(0)
        return self._buffer.write(buf)


class WebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        logging.info("Serving client")
        while 1:
            try:
                self.write_message(bytes(frames.get()), True)
                frames.task_done()
            except tornado.websocket.WebSocketClosedError:
                logging.info("Client disconnected")
                break
            except:
                logging.error("exc", exc_info=True)
                break



def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
        camera.start_recording(StreamingOutput(), format='mjpeg')
        camera.rotation = 180
        handlers = [(r"/ws", WebSocket)]
        application = tornado.web.Application(handlers)
        application.listen(8000)

        try:
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            logging.info("CTRL+C detected.")
        finally:
            camera.stop_recording()
            logging.info("Streaming Stopped.")


if __name__ == "__main__":
    main()
