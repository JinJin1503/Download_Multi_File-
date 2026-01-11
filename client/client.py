import socket
from shared.protocol import Protocol

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

def client_protocol_test():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Đã kết nối server")

        filename = input("Nhập tên file cần tải: ")

        request = Protocol.create_download_request(filename)
        encoded_request = Protocol.encode_message(request)

        client_socket.sendall(encoded_request)
        print("Đã gửi yêu cầu:", request)

        response = Protocol.receive_message(client_socket)

        if response is None:
            print("Server không phản hồi")
            return

        print("Header nhận được:", response)

        if response.startswith("FILE"):
            fname, fsize, status = Protocol.parse_file_header(response)
            print(f"Server OK - File: {fname}, Size: {fsize} bytes")

        elif response.startswith("ERROR"):
            print("Server báo lỗi: File không tồn tại")

        else:
            print("Phản hồi không hợp lệ")

    except Exception as e:
        print("Lỗi client:", e)

    finally:
        client_socket.close()
        print("Đóng kết nối")

if __name__ == "__main__":
    client_protocol_test()
