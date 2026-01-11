import socket
import os
import threading
from shared.protocol import Protocol, BUFFER_SIZE, STATUS_OK
from download_status import DownloadStatus
from status_handler import update_status

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(SAVE_DIR, exist_ok=True)

SOCKET_TIMEOUT = 10

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

            update_status(filename, DownloadStatus.SUCCESS, 100)

        except IOError as e:
            update_status(filename, DownloadStatus.ERROR)

    except socket.timeout:
        update_status(filename, DownloadStatus.ERROR)

    except ConnectionRefusedError:
        update_status(filename, DownloadStatus.ERROR)

    except Exception as e:
        print(f"[{filename}] Loi khong xac dinh:", e)

    finally:
        if sock:
            sock.close()


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
