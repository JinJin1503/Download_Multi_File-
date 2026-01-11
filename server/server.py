import socket
import os
import sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.protocol import Protocol

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
BUFFER_SIZE = 4096

def handle_client_worker(client_socket, client_addr):
    try:
        print(f"[Server] Kết nối mới từ: {client_addr}")

        raw_message = Protocol.receive_message(client_socket)
        if raw_message is None: return


        filename = Protocol.parse_download_request(raw_message)
        print(f"[Server] Yêu cầu tải: {filename}")

        if filename:

            if os.path.exists(filename) and os.path.isfile(filename):

                filesize = os.path.getsize(filename)

                header_str = Protocol.create_file_header(filename, filesize)
                client_socket.sendall(Protocol.encode_message(header_str))
                print(f"[Server] --> Gửi Header: {header_str}")

                print(f"[Server] --> Đang stream file ({filesize} bytes)...")
                sent_bytes = 0

                with open(filename, "rb") as f:
                    while True:

                        chunk = f.read(BUFFER_SIZE)

                        if not chunk:
                            break

                        client_socket.sendall(chunk)
                        sent_bytes += len(chunk)

                print(f"[Server] --> Hoàn tất gửi: {sent_bytes}/{filesize} bytes.")

            else:

                error_str = Protocol.create_error_message(filename)
                client_socket.sendall(Protocol.encode_message(error_str))
                print(f"[Server] --> Gửi lỗi 404: {filename}")
        else:
            print("[Server] Sai protocol.")

    except Exception as e:
        print(f"[Server] Lỗi: {e}")
    finally:
        client_socket.close()
        print(f"[Server] Đóng kết nối {client_addr}")


def main():
    print("--- SERVER PHASE 3: FILE STREAMING ---")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        print(f"[*] Lắng nghe tại {SERVER_HOST}:{SERVER_PORT}...")

        while True:
            client_socket, client_addr = server_socket.accept()

            handle_client_worker(client_socket, client_addr)

    except KeyboardInterrupt:
        print("\n[!] Tắt Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()