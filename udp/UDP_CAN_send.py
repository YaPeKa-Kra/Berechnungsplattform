import socket
import struct
import time

sock = socket.socket(socket.AF_INET,  # IPV4
                     socket.SOCK_DGRAM)  # UDP
TARGET_IP = "192.168.1.100"
TARGET_PORT = 5005

"""
Send CAN message over UDP. Descriptions:
can_id: 11-bit identifier
can_dlc: data length code (0-8)
can_flags: special flags (not used here, set to 0)
can_data: up to 8 bytes of data"
timestamp: timestamp (ms or mcs)
"""

while True:
    can_id = 0x123
    can_dlc = 4
    can_flags = 0b00000000 # standard frame, no RTR
    can_data = bytes([0x11, 0x22, 0x33]) + b'\x00' *4  # pad to 8 bytes
    timestamp = int(time.time() * 1000)  # current time in ms

    packet = struct.pack("!IBB8sI", 
                         can_id, 
                         can_dlc, 
                         can_flags, 
                         can_data, 
                         timestamp)
    
    sock.sendto(packet, (TARGET_IP, TARGET_PORT))
    time.sleep(1)  # wait 1 second before sending next message