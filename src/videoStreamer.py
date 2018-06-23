import io
import time
import logging
import queue
import socketserver
from http import server

try:
    import picamera
except ImportError:
    raise ImportError("Install picamera, example: #pip3 install picamera")

framesQueue = queue.Queue(5)


class StreamingOutput(object):
    _q = framesQueue

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
            self._q.put(self._buffer.getvalue())
            self._buffer.seek(0)
        return self._buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    _q = framesQueue

    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            while True:
                if self._q.empty():
                    continue
                frame = self._q.get()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
                self._q.task_done()

        else:  # Redirect all GET Requests to the stream
            self.send_response(301)
            self.send_header('Location', '/stream.mjpg')
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


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
        try:
            address = ('0.0.0.0', 8000)
            logging.info("Streaming started @ http://{}:{}/stream.mjpg".format(address[0], address[1]))
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("CTRL+C detected.")
        finally:
            camera.stop_recording()
            logging.info("Streaming Stopped.")


if __name__ == "__main__":
    main()
