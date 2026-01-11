import os
import sys

# Thêm thư mục cha của dự án vào sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))


import socket
import os
from shared.protocol import Protocol # Import class Protocol từ file dùng chung

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

def handle_client_worker(client_socket, client_addr):
    """
    Hàm xử lý Giao thức (Phase 2)
    Nhiệm vụ: Nhận Request -> Phân tích -> Trả về Header hoặc Error
    """
    try:
        print(f"[Server] Đang xử lý kết nối từ: {client_addr}")
        
        # 1. Nhận tin nhắn (Pseudo Code dòng 44)
        raw_message = Protocol.receive_message(client_socket)
        
        if raw_message is None:
            print("[Server] Client ngắt kết nối hoặc gửi tin rỗng.")
            return

        # 2. Phân tích yêu cầu (Pseudo Code dòng 48)
        # Input: "DOWNLOAD|a.txt" -> Output: "a.txt"
        filename = Protocol.parse_download_request(raw_message)
        print(f"[Server] Nhận yêu cầu tải file: '{filename}'")

        if filename:
            # 3. Kiểm tra sự tồn tại để quyết định Giao thức phản hồi
            if os.path.exists(filename) and os.path.isfile(filename):
                # --- TRƯỜNG HỢP CÓ FILE (Pseudo Code dòng 53-58) ---
                filesize = os.path.getsize(filename)
                
                # Tạo Header theo chuẩn: FILE|name|SIZE|bytes|STATUS|200
                header_str = Protocol.create_file_header(filename, filesize)
                
                # Đóng gói và gửi
                encrypted_header = Protocol.encode_message(header_str)
                client_socket.sendall(encrypted_header)
                
                print(f"[Server] --> Đã tìm thấy. Gửi Header: {header_str}")
                
            else:
                # --- TRƯỜNG HỢP KHÔNG CÓ FILE (Pseudo Code dòng 71-74) ---
                # Tạo thông báo lỗi: ERROR|name|404
                error_str = Protocol.create_error_message(filename)
                
                # Đóng gói và gửi
                encrypted_error = Protocol.encode_message(error_str)
                client_socket.sendall(encrypted_error)
                
                print(f"[Server] --> Không tìm thấy. Gửi Lỗi: {error_str}")
        else:
            print("[Server] Yêu cầu sai format protocol.")

    except Exception as e:
        print(f"[Server] Lỗi xử lý: {e}")
    finally:
        # Đóng kết nối ngay sau khi gửi phản hồi (cho giai đoạn này)
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
            # Gọi hàm xử lý trực tiếp (Chưa đa luồng, để test logic protocol cho kỹ)
            handle_client_worker(client_socket, client_addr)
            
    except KeyboardInterrupt:
        print("\n[!] Tắt Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()