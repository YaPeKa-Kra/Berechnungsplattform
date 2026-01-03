import socket
import time

# empfänger IP Adresse

TARGET_IP="192.168.1.100"
TARGET_PORT=5005

sock = socket.socket(socket.AF_INET, # IPV4
                     socket.SOCK_DGRAM) # UDP

while True:
    message = b"Hello, UDP Receiver!"
    sock.sendto(message, (TARGET_IP, TARGET_PORT))
    print(f"Sent message to {TARGET_IP}:{TARGET_PORT}")
    time.sleep(1)  # Warte 1 Sekunde vor dem nächsten Senden

de