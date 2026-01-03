import socket
import struct
import time

""" Broadcast UDP packets to all devices in subnet """

FMT = "<IBB8sI"  # Little-endian: can_id, can_dlc, can_flags, can_data(8 bytes), timestamp
Port = 5005
BROADCAST_IP = "255.255.255.255"

sock = socket.socket(socket.AF_INET,  # IPV4
                     socket.SOCK_DGRAM)  # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
start_time = time.time()

while True:
    can_id = 0x123
    can_dlc = 4
    can_flags = 0b00000000 # standard frame, no RTR
    can_data = bytes([0x11, 0x22, 0x33]) + b'\x00' *4  # pad to 8 bytes
    timestamp = int((time.time()-start_time)*1000) # current time in ms

    packet = struct.pack(FMT, 
                         can_id, 
                         can_dlc, 
                         can_flags, 
                         can_data, 
                         timestamp)
    
    sock.sendto(packet, (BROADCAST_IP, Port))
    time.sleep(1)  # wait 1 second before sending next message