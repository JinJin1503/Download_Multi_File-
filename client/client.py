import socket
import os
from shared.protocol import Protocol, BUFFER_SIZE

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

SAVE_DIR = "downloads"
os.makedirs(SAVE_DIR, exist_ok=True)


def download_file(filename):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("Da ket noi server")

        request = Protocol.create_download_request(filename)
        sock.sendall(Protocol.encode_message(request))
        print("Da gui yeu cau:", request)

        header = Protocol.receive_message(sock)
        if header is None:
            print("Server khong phan hoi")
            return

        if header.startswith("ERROR"):
            print("File khong ton tai tren server:", filename)
            return

        parsed_data = Protocol.parse_file_header(header)
        if not parsed_data:
            print("Header khong hop le:", header)
            return
        
        name, filesize, status = parsed_data

        if status != "200":
            print("Loi khi tai file:", status)
            return
        
        save_path = os.path.join(SAVE_DIR, name)
        with open(save_path, "wb") as f:
            ok = Protocol.receive_file_content(sock, f, filesize)

        if ok:
            print("Tai thanh cong:", name)
        else:
            print("Tai that bai:", name)

    except Exception as e:
        print("Loi:", e)

    finally:
        if sock:
            sock.close()
        print("Dong ket noi\n")


def main():
    print("Nhap danh sach file can tai (cach nhau boi dau phay)")
    files = input(">> ").split(",")

    for f in files:
        filename = f.strip()
        if filename:
            download_file(filename)


if __name__ == "__main__":
    main()
