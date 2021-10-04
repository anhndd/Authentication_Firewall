from http.server import BaseHTTPRequestHandler, HTTPServer
from login import isLoginSuccess
import ssl, os
import urllib.parse
import subprocess

# Request Handler class
class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        f = open("./head.html", "rb")
        self.wfile.write(f.read())
        f = open("./body.html", "rb")
        self.wfile.write(f.read())
        f.close()
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Get data size
        post_data = self.rfile.read(content_length)  # Get data content
        data_list = post_data.decode("utf-8").split("&")
        username = data_list[0].split("=")[1]
        password = data_list[1].split("=")[1]
        ipsource = self.client_address[0]
        print("Username: " + username)
        print("Password: " + urllib.parse.unquote(password))
        print("ip address: " + ipsource)

        messSucc = b"<div class=\"alert success\"><span class=\"closebtn\" onclick=\"this.parentElement.style.display='none';\">&times;</span>" \
                   b"<strong>Success!</strong> Welcome to the internet</div>"
        messFail = b"<div class=\"alert \"><span class=\"closebtn\" onclick=\"this.parentElement.style.display='none';\">&times;</span>" \
                   b"<strong>Alert!</strong> Wrong Username or Password.</div>"

        self._set_response()
        f = open("./head.html", "rb")
        self.wfile.write(f.read())

        loginSuccess = isLoginSuccess("https://cas.unilim.fr", username, urllib.parse.unquote(password))
        if loginSuccess:
            self.wfile.write(messSucc)
            r = subprocess.run('sudo iptables -t nat -I PREROUTING -s ' + ipsource + ' -j ACCEPT',shell=True,stdout=subprocess.PIPE) # Récupère la sortie d'une commande
            r = subprocess.run('sudo iptables -t nat -A POSTROUTING -s ' + ipsource + ' -j MASQUERADE',shell=True,stdout=subprocess.PIPE) # Récupère la sortie d'une commande
            r = subprocess.run('sudo iptables -t filter -A FORWARD -s ' + ipsource + ' -m state --state NEW -j ACCEPT',shell=True,stdout=subprocess.PIPE) # Récupère la sortie d'une commande
            print(r.stdout)
        else:
            self.wfile.write(messFail)
        f = open("./body.html", "rb")
        self.wfile.write(f.read())
        f.close()
        return

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('10.10.10.1', port)
    httpd = server_class(server_address, handler_class)

    # Implement SSL certificate
    # httpd.socket = ssl.wrap_socket(
    #     httpd.socket,
    #     keyfile="./server.key",
    #     certfile='./server.crt',
    #     server_side=True)

    print('Starting httpd...')
    print(httpd)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
