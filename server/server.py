import socket
import os
import sys
import threading
from shared.protocol import Protocol

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILE_DIR, exist_ok=True)

def handle_client_worker(client_socket, client_addr):
    thread_id = threading.get_ident()
    try:
        print(f"[Thread-{thread_id}] Kết nối từ {client_addr}")

        client_socket.settimeout(SOCKET_TIMEOUT)

        raw_message = Protocol.receive_message(client_socket)
        if raw_message is None:
            print(f"[Thread-{thread_id}] Client chủ động ngắt kết nối.")
            return

        filename = Protocol.parse_download_request(raw_message)
        print(f"[Thread-{thread_id}] Yêu cầu tải: {filename}")
        # 1. Nếu là yêu cầu lấy danh sách (LIST)
        if raw_message == "LIST":
            print(f"[Thread-{thread_id}] Yêu cầu lấy danh sách file")
            try:
                # Lấy tất cả file trong thư mục, bỏ qua file ẩn
                files = [f for f in os.listdir(FILE_DIR) if os.path.isfile(os.path.join(FILE_DIR, f)) and not f.startswith('.')]
                response = Protocol.create_list_response(files)
                client_socket.sendall(Protocol.encode_message(response))
                print(f"[Thread-{thread_id}] Đã gửi danh sách: {len(files)} files")
            except Exception as e:
                print(f"[Thread-{thread_id}] Lỗi lấy danh sách: {e}")
            return # Xử lý xong thì thoát thread này (Client sẽ kết nối lại để tải sau)
        
        if filename:
            safe_filename = os.path.basename(filename) 
            file_path = os.path.join(FILE_DIR, safe_filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                filesize = os.path.getsize(file_path)

                header_str = Protocol.create_file_header(safe_filename, filesize)
                client_socket.sendall(Protocol.encode_message(header_str))

                print(f"[Thread-{thread_id}] Đang gửi file...")
                with open(file_path, "rb") as f:
                    sent_bytes = 0
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk: break

                        try:
                            client_socket.sendall(chunk)
                            sent_bytes += len(chunk)
                        except (ConnectionResetError, BrokenPipeError):
                            print(f"[Thread-{thread_id}] ⚠️ Client ngắt kết nối giữa chừng!")
                            return

                print(f"[Thread-{thread_id}] --> Hoàn tất gửi: {sent_bytes}/{filesize} bytes")
            else:

                error_str = Protocol.create_error_message(safe_filename)
                client_socket.sendall(Protocol.encode_message(error_str))
                print(f"[Thread-{thread_id}] --> Gửi lỗi 404 (File not found).")
        else:
            error_str = Protocol.create_error_message("INVALID_REQUEST")
            client_socket.sendall(Protocol.encode_message(error_str))
            return
        
    except socket.timeout:
        print(f"[Thread-{thread_id}] ⚠️ Lỗi Timeout: Client quá lâu không phản hồi.")
    except Exception as e:
        print(f"[Thread-{thread_id}] ⚠️ Lỗi ngoại lệ: {e}")
    finally:
        client_socket.close()
        print(f"[Thread-{thread_id}] Đã giải phóng tài nguyên.")

def main():
    print(f"--- SERVER FINAL (TIMEOUT={SOCKET_TIMEOUT}s) ---")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(10)
        print(f"[*] Sẵn sàng tại {SERVER_HOST}:{SERVER_PORT}")

        while True:
            client_socket, client_addr = server_socket.accept()

            t = threading.Thread(target=handle_client_worker, args=(client_socket, client_addr))
            t.daemon = True
            t.start()

    except KeyboardInterrupt:
        print("\n[!] Tắt Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()