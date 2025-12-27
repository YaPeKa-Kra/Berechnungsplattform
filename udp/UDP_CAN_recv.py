import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))

while True:
    data, addr = sock.recvfrom(1024)

    can_id, dlc, flags, payload, timestamp = struct.unpack("<IBB8sI", data)

    can_data = payload[:dlc]

    print(f"ID=0x{can_id:X} DLC={dlc} DATA={can_data.hex()} TIME={timestamp}")
