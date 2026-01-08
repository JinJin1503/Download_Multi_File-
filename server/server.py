import socket


SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

def main():
    print(f"--- SERVER KHỞI ĐỘNG ---")


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:

        server_socket.bind((SERVER_HOST, SERVER_PORT))


        server_socket.listen(5)
        print(f"[*] Đang lắng nghe tại {SERVER_HOST}:{SERVER_PORT}...")
        print("[*] Nhấn Ctrl+C để tắt Server.")


        while True:

            client_socket, client_addr = server_socket.accept()

            print(f"[+] Có kết nối mới từ: {client_addr}")

            client_socket.close()

    except KeyboardInterrupt:
        print("\n[!] Đã tắt Server thủ công.")
    except Exception as e:
        print(f"[!] Lỗi Server: {e}")
    finally:
        server_socket.close()
        print("--- SERVER ĐÃ ĐÓNG ---")

if __name__ == "__main__":
    main()