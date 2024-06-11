
import logging
logging.getLogger("scapy").setLevel(logging.CRITICAL)
import socket
from scapy.packet import Raw
from scapy.all import conf, hexdump, Packet, ByteField, ShortField
import requests

# conf.iface = 'en0'
COTP_PACKET = b'\x03\x00\x00\x16\x11\xe0\x00\x00\x00\x05\x00\xc1\x02\x01\x00\xc2\x02\x02\x00\xc0\x01\x0a'
ROSCTR_SETUP = b'\x03\x00\x00\x19\x02\xf0\x80\x32\x01\x00\x00\x00\x00\x00\x08\x00\x00\xf0\x00\x00\x01\x00\x01\x01\xe0'
FIRST_SZL_REQ = b'\x03\x00\x00\x21\x02\xf0\x80\x32\x07\x00\x00\x00\x00\x00\x08\x00\x08\x00\x01\x12\x04\x11\x44\x01\x00\xff\x09\x00\x04\x00\x11\x00\x01'
SECOND_SZL_REQ = b'\x03\x00\x00\x21\x02\xf0\x80\x32\x07\x00\x00\x00\x00\x00\x08\x00\x08\x00\x01\x12\x04\x11\x44\x01\x00\xff\x09\x00\x04\x00\x1c\x00\x01'

HARDWARE_OFFSET = 73
SERIAL_NUM_OFFSET = 175

RECV_SIZE = 1024 * 8


class TPKT(Packet):
    name = "TPKT"
    fields_desc = [ByteField("version", 3),
                   ByteField("reserved", 0),
                   ShortField("length", 0x0016)]


def get_string(packet, offset):
    cont = 0
    for b in packet.load[offset:]:
        if b != 0:
            cont += 1
        else:
            break
    return packet.load[offset:offset+cont].decode('ascii', errors='ignore').strip()


def get_s7_MODBUS_info(ip):
    target = (ip, 102)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(target)

        cotp_packet = Raw(load=COTP_PACKET)
        sock.send(bytes(cotp_packet))
        cotp_resp = sock.recv(RECV_SIZE)
        # print('COTP Response:')
        # hexdump(cotp_resp)

        rosctr_setup = Raw(load=ROSCTR_SETUP)
        sock.send(bytes(rosctr_setup))
        rosctr_setup_resp = sock.recv(RECV_SIZE)
        # print('ROSCTR Setup Response:')
        # hexdump(rosctr_setup_resp)

        szl_req = Raw(load=FIRST_SZL_REQ)
        sock.send(bytes(szl_req))
        szl_resp = sock.recv(RECV_SIZE)
        # print('First SZL Response:')
        # hexdump(szl_resp)

        second_szl_req = Raw(load=SECOND_SZL_REQ)
        sock.send(bytes(second_szl_req))
        second_szl_resp = sock.recv(RECV_SIZE)
        # print('Second SZL Response:')
        # hexdump(second_szl_resp)
        return second_szl_resp
    except Exception as error:
        # logging.error(f'Error occurred: {error}')
        pass
    finally:
        sock.close()
    return None


def http_match(ip):
    try:
        response = requests.get(f'http://{ip}:80/index.html', timeout=5)
        last_modified_header = response.headers.get('Last-Modified', 'Unknown')
        http_fingerprint = 'Tue, 19 May 1993 09:00:00 GMT'
        # print(f"HTTP Last-Modified: {last_modified_header}")
        if response.status_code == 200 and http_fingerprint in last_modified_header:
            return True
    except Exception as e:
        # print(f"Error connecting to {ip}: {e}")
        pass
    return False


def s7_MODBUS_match(ip):
    result = [False, False]

    serial_fingerprint = '88111222'
    hardware_fingerprint = 'Siemens, SIMATIC, S7-200'
    try:
        response = get_s7_MODBUS_info(ip)
        if response:
            p = Raw(response)
            serial_num = get_string(p, SERIAL_NUM_OFFSET)
            hardware = get_string(p, HARDWARE_OFFSET)
            # print(f'Serial Number: {serial_num}')
            # print(f'Hardware: {hardware}')
            if serial_fingerprint in serial_num:
                result[0] = True
            if hardware_fingerprint in hardware:
                result[1] = True
    except Exception as e:
        # print(f"Error connecting to {ip}: {e}")
        pass
    return result


def main(ip):
    result = []
    result.append(http_match(ip))
    s7_result = s7_MODBUS_match(ip)
    result.append(s7_result[0])
    result.append(s7_result[1])
    return result


if __name__ == "__main__":

    result = main("127.0.0.1")

    print(result)
