import socket
from shared.protocol import Protocol, STATUS_OK

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def download_file(filename):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Da ket noi server")

        request = Protocol.create_download_request(filename)
        client_socket.sendall(Protocol.encode_message(request))
        print("Da gui yeu cau:", request)

        response = Protocol.receive_message(client_socket)
        if response is None:
            print("Server khong phan hoi")
            return

        server_filename, file_size, status = Protocol.parse_file_header(response)

        if status != STATUS_OK:
            print("File khong ton tai tren server")
            return

        print("Bat dau tai file:", server_filename)
        print("Kich thuoc:", file_size, "bytes")

        with open(server_filename, "wb") as f:
            success = Protocol.receive_file_content(client_socket, f, file_size)

        if success:
            print("Tai file thanh cong")
        else:
            print("Tai file that bai")

    except Exception as e:
        print("Loi:", e)

    finally:
        client_socket.close()
        print("Dong ket noi")


if __name__ == "__main__":
    filename = input("Nhap ten file can tai: ")
    download_file(filename)
