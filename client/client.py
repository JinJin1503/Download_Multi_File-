import socket

def main():
    SERVER_IP = "127.0.0.1"   
    SERVER_PORT = 5000

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client: Da tao socket")

        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Client: Da ket noi toi Server")

        message = "HELLO SERVER"
        client_socket.sendall(message.encode("utf-8"))
        print("Client: Da gui ->", message)

        response = client_socket.recv(1024)
        if not response:
            print("Client: Khong nhan duoc phan hoi")
        else:
            print("Client: Nhan tu Server ->", response.decode("utf-8"))

    except Exception as e:
        print("Client: Loi xay ra:", e)

    finally:
        client_socket.close()
        print("Client: Da dong ket noi")

if __name__ == "__main__":
    main()
