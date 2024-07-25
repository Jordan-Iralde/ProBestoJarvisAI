import socket
import struct

def wake_on_lan(mac_address):
    if len(mac_address) == 17:
        mac_address = mac_address.replace(mac_address[2], '')
    data = ''.join(['FFFFFFFFFFFF', mac_address * 16])
    send_data = b''
    for i in range(0, len(data), 2):
        send_data += struct.pack('B', int(data[i: i + 2], 16))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 7))
