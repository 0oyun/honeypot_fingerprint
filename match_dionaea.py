import requests
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import ftplib
from pymemcache.client import base


def get_certificate(hostname, port=443):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=hostname,
        )

        conn.settimeout(5.0)
        conn.connect((hostname, port))

        cert_bin = conn.getpeercert(binary_form=True)
        cert_pem = ssl.DER_cert_to_PEM_cert(cert_bin)
        conn.close()

        return cert_pem
    except Exception as e:
        # print(f"Could not connect to {hostname}:{port}: {e}")
        return None


def parse_certificate(cert_pem):
    try:
        cert = x509.load_pem_x509_certificate(
            cert_pem.encode(), default_backend())

        cert_info = {
            "subject": cert.subject,
            "issuer": cert.issuer,
            "serial_number": cert.serial_number,
            "not_valid_before": cert.not_valid_before_utc,
            "not_valid_after": cert.not_valid_after_utc,
            "version": cert.version.name,
            "signature_algorithm": cert.signature_algorithm_oid._name,
            "extensions": {ext.oid._name: ext.value for ext in cert.extensions},
        }

        return cert_info
    except Exception as e:
        # print(f"Could not parse certificate: {e}")
        return None


def connect_ftp(server, port, username, password):
    # Connect to the FTP server
    ftp = ftplib.FTP()
    ftp.connect(server, port)
    ftp.login(username, password)
    return ftp


def close_ftp(ftp):
    # Close the FTP connection
    ftp.quit()


def receive_all(sock):
    """
    Helper function to receive all data from the socket.
    """
    buffer_size = 4096
    data = b''

    while True:
        try:
            part = sock.recv(buffer_size)
            if not part:
                break
            data += part
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

    return data


def http_match(ip):
    try:
        response = requests.get(f'http://{ip}:80', timeout=5)
        http_fingerprint = b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>\n<title>Directory listing for /</title>\n<body>\n<h2>Directory listing for /</h2>\n<hr>\n<ul>\n<li><a href="../">../</a>\n</ul>\n<hr>\n</body>\n</html>\n'
        if response.status_code == 200 and http_fingerprint in response.content:
            return True
    except Exception as e:
        # print(f"Error connecting to {ip}: {e}")
        pass
    return False


def ftp_match(ip):
    try:
        ftp = connect_ftp(ip, 21, 'anonymous', '')
        ftp_fingerprint = b"220 DiskStation FTP server ready."
        response = ftp.getwelcome().encode()
        if ftp_fingerprint in response:
            return True
    except Exception as e:
        # print(f"Error connecting to {ip}: {e}")
        pass
    return False


def memcache_match(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, 11211))
        s.send(b'stats\r\n')
        data = receive_all(s)
        # print(data)
        memcached_fingerprint_1 = b"STAT version 1.4.25\r\n"
        memcached_fingerprint_2 = b"STAT rusage_user 0.550000\r\n"
        memcached_fingerprint_3 = b"STAT pointer_size 64\r\n"
        if memcached_fingerprint_1 in data and memcached_fingerprint_2 in data and memcached_fingerprint_3 in data:
            return True

    except Exception as e:
        # print(f"Error connecting to {ip}: {e}")
        pass
    return False


def ssl_match(ip):
    try:
        cert_pem = get_certificate(ip)
        cert_info = parse_certificate(cert_pem)
        if cert_info["subject"].get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value == 'dionaea.carnivore.it' \
                and cert_info["subject"].get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value == 'Nepenthes Development Team':
            return True
    except Exception as e:
        # print(f"Error connecting to {ip}: {e}")
        pass
    return False


def main(ip):
    result = []
    result.append(http_match(ip))
    result.append(ftp_match(ip))
    result.append(memcache_match(ip))
    result.append(ssl_match(ip))
    return result
