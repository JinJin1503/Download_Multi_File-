import socket
import os
import threading
from shared.protocol import Protocol, BUFFER_SIZE, STATUS_OK

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(SAVE_DIR, exist_ok=True)

SOCKET_TIMEOUT = 10

def download_file(filename):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SOCKET_TIMEOUT)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"[{filename}] Da ket noi server")

        request = Protocol.create_download_request(filename)
        sock.sendall(Protocol.encode_message(request))
        print(f"[{filename}] Da gui yeu cau")

        header = Protocol.receive_message(sock)
        if header is None:
            print(f"[{filename}] Server khong phan hoi")
            return

        if header.startswith("ERROR"):
            print(f"[{filename}] File khong ton tai tren server")
            return

        name, filesize, status = Protocol.parse_file_header(header)
        if name is None:
            print(f"[{filename}] Header khong hop le")
            return

        if status != STATUS_OK:
            print(f"[{filename}] Loi trang thai:", status)
            return

        save_path = os.path.join(SAVE_DIR, name)

        try:
            with open(save_path, "wb") as f:
                ok = Protocol.receive_file_content(sock, f, filesize)
        except IOError:
            print(f"[{filename}] Loi: Khong ghi duoc file")
            return

        if ok:
            print(f"[{filename}] Tai thanh cong")
        else:
            print(f"[{filename}] Tai that bai")

    except socket.timeout:
        print(f"[{filename}] Loi: Het thoi gian cho server")

    except ConnectionRefusedError:
        print(f"[{filename}] Loi: Khong ket noi duoc server")

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

    print("\nTat ca file da tai xong")


if __name__ == "__main__":
    main()
