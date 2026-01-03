import socket

IP = "0.0.0.0"  # All available network interfaces
PORT = 5005

sock = socket.socket(socket.AF_INET,  # IPV4
                     socket.SOCK_DGRAM)  # UDP
sock.bind((IP, PORT))

print(f"Listening for UDP packets on {IP}:{PORT}")

while True:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    print(f"Received message from {addr}: {data.decode()}")