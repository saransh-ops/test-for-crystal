import ssl
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Generate self-signed cert
if not os.path.exists("cert.pem"):
    print("Generating self-signed certificate...")
    from OpenSSL import crypto
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    c = crypto.X509()
    c.get_subject().CN = "localhost"
    c.set_serial_number(1)
    c.gmtime_adj_notBefore(0)
    c.gmtime_adj_notAfter(365 * 24 * 60 * 60)
    c.set_issuer(c.get_subject())
    c.set_pubkey(k)
    c.sign(k, "sha256")
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, c))
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    print("Certificate generated.")

server = HTTPServer(("localhost", 8443), SimpleHTTPRequestHandler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain("cert.pem", "key.pem")
server.socket = ctx.wrap_socket(server.socket, server_side=True)
print("\nServing on https://localhost:8443")
print("Open: https://localhost:8443/report-web.html")
print("Browser will warn about self-signed cert — click Advanced > Proceed\n")
server.serve_forever()