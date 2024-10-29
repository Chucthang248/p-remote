import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("Server started...")
    while True:
        client, addr = server.accept()
        print(f"Connected by {addr}")
        command = client.recv(1024).decode()
        # Xử lý lệnh ở đây (chẳng hạn, liệt kê ứng dụng)
        response = "List of applications"
        client.send(response.encode())
        client.close()

start_server()