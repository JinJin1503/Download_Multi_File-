import socket
import os
import threading
import sys  
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.protocol import Protocol, BUFFER_SIZE, STATUS_OK
from download_status import DownloadStatus
from status_handler import update_status

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(SAVE_DIR, exist_ok=True)

SOCKET_TIMEOUT = 10

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None
    
def download_file(filename):
    sock = None
    try:
        update_status(filename, DownloadStatus.CONNECTING)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SOCKET_TIMEOUT)
        sock.connect((SERVER_HOST, SERVER_PORT))
        update_status(filename, DownloadStatus.REQUESTING)

        request = Protocol.create_download_request(filename)
        sock.sendall(Protocol.encode_message(request))

        header = Protocol.receive_message(sock)
        if header is None:
            update_status(filename, DownloadStatus.ERROR)
            return

        if header.startswith("ERROR"):
            update_status(filename, DownloadStatus.NOT_FOUND)
            return

        name, filesize, status = Protocol.parse_file_header(header)
        if name is None:
            update_status(filename, DownloadStatus.ERROR)
            return

        if status != STATUS_OK:
            update_status(filename, DownloadStatus.ERROR)
            return

        save_path = os.path.join(SAVE_DIR, name)
        received = 0
        
        try:
            with open(save_path, "wb") as f:
                update_status(filename, DownloadStatus.DOWNLOADING, 0)

                last_percent = -1

                while received < filesize:
                    chunk = sock.recv(min(BUFFER_SIZE, filesize - received))
                    if not chunk:
                        update_status(filename, DownloadStatus.ERROR)
                        return

                    f.write(chunk)
                    received += len(chunk)

                    if filesize > 0:
                        percent = int((received / filesize) * 100)
                        if percent != last_percent:
                            update_status(filename, DownloadStatus.DOWNLOADING, percent)
                            last_percent = percent

            update_status(filename, DownloadStatus.VERIFYING)
            
            server_checksum = sock.recv(32).decode('utf-8')
            
            local_checksum = calculate_md5(save_path)
            
            if local_checksum and local_checksum == server_checksum:
                update_status(filename, DownloadStatus.SUCCESS, 100)
            else:
                print(f"Lỗi checksum: Server={server_checksum} vs Local={local_checksum}")
                update_status(filename, DownloadStatus.CORRUPTED)

        except IOError as e:
            update_status(filename, DownloadStatus.IO_ERROR)

    except socket.timeout:
        update_status(filename, DownloadStatus.TIMEOUT)

    except ConnectionRefusedError:
        update_status(filename, DownloadStatus.DISCONNECT)

    except Exception as e:
        update_status(filename, DownloadStatus.ERROR)

    finally:
        if sock:
            sock.close()

def get_server_file_list():
    """Hàm kết nối server chỉ để lấy danh sách file"""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5) 
        sock.connect((SERVER_HOST, SERVER_PORT))
        
        # Gửi lệnh LIST
        req = Protocol.create_list_request()
        sock.sendall(Protocol.encode_message(req))
        
        # Nhận phản hồi
        msg = Protocol.receive_message(sock)
        if msg:
            return Protocol.parse_list_response(msg)
        return []
    except Exception as e:
        print("Lỗi lấy danh sách file:", e)
        return []
    finally:
        if sock: sock.close()

def main():
    print("Nhap danh sach file can tai (cach nhau boi dau phay)")
    files = input(">> ").split(",")

    threads = []

    for f in files:
        filename = f.strip()
        if filename:
            t = threading.Thread(target=download_file, args=(filename,))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    print("\nTat ca file da duoc xu ly")


if __name__ == "__main__":
    main()
