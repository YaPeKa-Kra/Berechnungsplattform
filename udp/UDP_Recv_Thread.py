import socket
import struct
import queue
import threading
import csv
import datetime

logfile = open("udp_log.csv", "a", newline="")
csv_writer = csv.writer(logfile)

csv_writer.writerow([
    "timestamp",
    "can_id",
    "dlc",
    "flags",
    "can_data"
    ])
logfile.flush()

def test_handler_1(can_data):
    data_handler_1= can_data[0]
    print("Data:", data_handler_1)

def test_handler_2(can_data):
    data_handler_2= int.from_bytes(can_data[:2], "little", signed = True)
    print("Data:", data_handler_2)

DISPATCH_TABLE = {
    0x123: test_handler_1,
    0x456: test_handler_2,
}

FMT = "!IBB8sI"  # Big-endian: can_id, can_dlc, can_flags, can_data(8 bytes), timestamp 
PORT = 5005

recv_queue = queue.Queue(maxsize=1000)

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))

    while True:
        raw, addr = sock.recvfrom(1024) # recvfrom return a tuple consisting off rawvalue and sender address, Buffer size is 1024 bytes
        frame = struct.unpack(FMT, raw)
        recv_queue.put(frame)

def csv_logger(can_id, dlc, flags, can_data):
    csv_writer.writerow([
        datetime.datetime.now().isoformat(),
        hex(can_id),
        dlc,
        flags,
        can_data.hex()
    ])
    logfile.flush()

def udp_processor():
    while True:
        # takes next entry from queue (blocking)
        frame = recv_queue.get()
        can_id, dlc, flags, data, timestamp = frame
        can_data = data[:dlc]
        print(f"ID=0x{can_id:X} DLC={dlc} DATA={can_data.hex()} TIME={timestamp}")

        handler = DISPATCH_TABLE.get(can_id)
        if handler:
            handler(can_data)

        csv_logger(can_id, dlc, flags, can_data)


threading.Thread(target=udp_listener, daemon=True).start()
threading.Thread(target=udp_processor, daemon=True).start()

while True:
    pass