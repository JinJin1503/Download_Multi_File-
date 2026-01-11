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
    """
    Hàm này sẽ chạy trên một LUỒNG RIÊNG (Thread)
    Mỗi client kết nối sẽ có 1 hàm này chạy song song.
    """
    try:

        thread_id = threading.get_ident()
        print(f"[Thread-{thread_id}] Bắt đầu xử lý: {client_addr}")

        raw_message = Protocol.receive_message(client_socket)
        if raw_message is None:
            print(f"[Thread-{thread_id}] Client ngắt kết nối.")
            return


        filename = Protocol.parse_download_request(raw_message)
        print(f"[Thread-{thread_id}] Yêu cầu tải: {filename}")

        if filename:

            if os.path.exists(filename) and os.path.isfile(filename):
                filesize = os.path.getsize(filename)

                header_str = Protocol.create_file_header(filename, filesize)
                client_socket.sendall(Protocol.encode_message(header_str))

                print(f"[Thread-{thread_id}] Đang gửi file...")
                with open(filename, "rb") as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk: break
                        client_socket.sendall(chunk)

                print(f"[Thread-{thread_id}] --> Gửi xong file cho {client_addr}")

            else:

                error_str = Protocol.create_error_message(filename)
                client_socket.sendall(Protocol.encode_message(error_str))
                print(f"[Thread-{thread_id}] --> Lỗi 404 sent.")
        else:
            print(f"[Thread-{thread_id}] Sai format.")

    except Exception as e:
        print(f"[Thread-{thread_id}] Lỗi ngoại lệ: {e}")
    finally:

        client_socket.close()
        print(f"[Thread-{thread_id}] Giải phóng kết nối {client_addr}")

def main():
    print("--- SERVER PHASE 4: MULTI-THREADING (READY FOR 10+ CLIENTS) ---")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(10)
        print(f"[*] Server lắng nghe tại {SERVER_HOST}:{SERVER_PORT}")

        while True:

            client_socket, client_addr = server_socket.accept()
            print(f"[Main] Có khách mới: {client_addr}")

            t = threading.Thread(target=handle_client_worker, args=(client_socket, client_addr))
            t.daemon = True
            t.start()

    except KeyboardInterrupt:
        print("\n[!] Tắt Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()