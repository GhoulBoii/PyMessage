from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


# Define the handler to handle requests
class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - %s" % (self.address_string(), format % args))


# Start a local HTTP server
def start_http_server(port):
    server_address = ("", port)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)  # Use custom handler
    print(f"HTTP server started at port {port}")
    return httpd


def main():
    PORT = 8000
    logging.basicConfig(filename=f"{SCRIPT_DIR}/email_seen.log", level=logging.INFO)
    sys.stdout = open(f"{SCRIPT_DIR}/email_seen.log", "a")
    httpd = start_http_server(PORT)
    try:
        # Keep the program running until interrupted
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Close the HTTP server when interrupted
        httpd.shutdown()
        print("HTTP server stopped")


if __name__ == "__main__":
    main()
