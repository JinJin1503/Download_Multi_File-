import socket

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print("Server dang lang nghe...")

while True:
    client_socket, client_addr = server_socket.accept()
    print("Server: Co ket noi tu", client_addr)

    data = client_socket.recv(1024)
    if data:
        print("Server nhan:", data.decode("utf-8"))

        reply = "HELLO CLIENT"
        client_socket.sendall(reply.encode("utf-8"))

    client_socket.close()
    print("Server: Dong ket noi voi client")
