import http.server
import socketserver
import requests
from urllib.parse import urljoin
import urllib

PORT = 1234  # Port on which your proxy server will run

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Decode the request path
        decoded_path = urllib.parse.unquote(self.path)
        target_url = urljoin('https://www.youtube.com', decoded_path)

        # Print the URL being requested
        print(f"Received request for: {target_url}")

        try:
            # Forward the request to YouTube
            response = requests.get(target_url, headers=self.headers, allow_redirects=True)

            # Print the response status code and content length
            print(f"Response status code: {response.status_code}")
            print(f"Content length: {len(response.content)} bytes")

            # Send the response back to the client
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.content)

            # Print completion message
            print(f"Request handling completed for: {target_url}")

        except requests.RequestException as e:
            # Print any request exceptions
            print(f"Request to {target_url} failed: {e}")
            self.send_error(500, "Internal Server Error")
            print(f"Request handling failed for: {target_url}")

        except Exception as e:
            # Print any general exceptions
            print(f"An unexpected error occurred: {e}")
            self.send_error(500, "Internal Server Error")
            print(f"Request handling failed for: {target_url}")

with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
