import socket
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.protocol import Protocol

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

def handle_client_worker(client_socket, client_addr):
    """
    Hàm xử lý Giao thức (Phase 2)
    Nhiệm vụ: Nhận Request -> Phân tích -> Trả về Header hoặc Error
    """
    try:
        print(f"[Server] Đang xử lý kết nối từ: {client_addr}")

        raw_message = Protocol.receive_message(client_socket)

        if raw_message is None:
            print("[Server] Client ngắt kết nối hoặc gửi tin rỗng.")
            return

        filename = Protocol.parse_download_request(raw_message)
        print(f"[Server] Nhận yêu cầu tải file: '{filename}'")

        if filename:

            if os.path.exists(filename) and os.path.isfile(filename):

                filesize = os.path.getsize(filename)

                header_str = Protocol.create_file_header(filename, filesize)

                encrypted_header = Protocol.encode_message(header_str)
                client_socket.sendall(encrypted_header)

                print(f"[Server] --> Đã tìm thấy. Gửi Header: {header_str}")

            else:

                error_str = Protocol.create_error_message(filename)

                encrypted_error = Protocol.encode_message(error_str)
                client_socket.sendall(encrypted_error)

                print(f"[Server] --> Không tìm thấy. Gửi Lỗi: {error_str}")
        else:
            print("[Server] Yêu cầu sai format protocol.")

    except Exception as e:
        print(f"[Server] Lỗi xử lý: {e}")
    finally:

        client_socket.close()
        print(f"[Server] Đóng kết nối với {client_addr}")

def main():
    print("--- SERVER PHASE 2: PROTOCOL HANDSHAKE ---")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        print(f"[*] Đang lắng nghe tại {SERVER_HOST}:{SERVER_PORT}...")

        while True:
            client_socket, client_addr = server_socket.accept()

            handle_client_worker(client_socket, client_addr)

    except KeyboardInterrupt:
        print("\n[!] Tắt Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()