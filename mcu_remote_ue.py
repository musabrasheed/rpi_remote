import RPi.GPIO as GPIO
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

host_name = '8.8.8.8'  # IP Address
host_port = 8000    # Port


def get_ip_address():
    testIP = "8.8.8.8"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((testIP, 0))
    ipaddr = s.getsockname()[0]
    host = socket.gethostname()
    print("IP:", ipaddr, " Host:", host)
    return ipaddr


host_name = get_ip_address()  # IP Address of Raspberry Pi


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(22, GPIO.OUT)  # Reset
    GPIO.setup(4, GPIO.OUT)  # Power


class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        os.path.abspath("mura/")
        html = '''
           <html>
           <head>
           <style>
               body, html {{height: 100%; margin: 0;}}
               .button {{ background-color: #107d69; border: none;
               color: white; padding: 15px; text-align: center;
               text-decoration: none; display: inline-block; font-size:
               12px; margin: 4px 2px; cursor: pointer; box-shadow: 0 5px #999; }}
               .button:hover {{background-color: #159e85}}
               .button {{border-radius: 12px;}}
               .button:active {{ background-color: #3e8e41; box-shadow: 0 5px #666; transform: translateY(4px); }}
               .bgimg {{ background-color: black;
               height: 100%; background-position: center; 
               background-size: cover;position: 
               relative;color: white;
               font-family: "Courier New", Courier,monospace;
               font-size: 25px;}}
               .topleft {{position: absolute;top: 0;left: 16px;}}
               .bottomleft {{position: absolute;bottom: 0;left: 16px;}}
               .middle {{position: absolute;top: 35%;left: 50%;transform: translate(-50%, -50%);text-align: center;}}
               .middleX {{position: absolute;top: 50%;left: 50%;transform: translate(-50%, -50%);text-align: center;}}

               hr {{margin: auto;width: 40%;}}
           </style>
           </head>
           <body>
           <div class="bgimg">
                <div class="topleft">
                    <p>u-blox</p>
                </div>
                <div class="middle">
                    <h1>Raspberry PI</h1>
                    <hr>
                    <p>Remote Dashboard</p>
                    <form action="/" method="POST">
                       <input class="button" type="submit" name="submit" value="Power">
                       <input class="button" type="submit" name="submit" value="Reset">
                    </form>
                    <br><h6>IP Address: {}<h6>
                </div>
            </div>
           </body>
           </html>
        '''
        html = html.format(get_ip_address())
        self.do_HEAD()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == 'Reset':
            GPIO.output(22, GPIO.LOW)
            time.sleep(1)
            GPIO.output(22, GPIO.HIGH)
            time.sleep(1)

        if post_data == 'Power':
            GPIO.output(4, GPIO.LOW)
            time.sleep(3)
            GPIO.output(4, GPIO.HIGH)

        print("Device {} button pressed!".format(post_data))
        self._redirect('/')  # Redirect back to the root url


if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


