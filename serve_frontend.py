"""
Kiwi Trails Frontend Development Server
"""
import http.server
import os
import socketserver

PORT = 5500
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


class KiwiTrailsHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_GET(self):
        # Redirect root / to /frontend/
        if self.path in ("", "/"):
            self.send_response(302)
            self.send_header("Location", "/frontend/")
            self.end_headers()
            return

        # Rewrite paths if requested without /frontend/ prefix
        for prefix in ("/css/", "/js/", "/pages/", "/assets/"):
            if self.path.startswith(prefix):
                self.path = "/frontend" + self.path
                break
        if self.path == "/index.html":
            self.path = "/frontend/index.html"

        return super().do_GET()


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), KiwiTrailsHandler) as httpd:
        print(f"Kiwi Trails Frontend running at http://127.0.0.1:{PORT}/frontend/")
        print("Serving files with full CSS and JavaScript support.")
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run_server()
