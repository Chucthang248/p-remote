import socket

def send_command(command):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('server_ip', 12345))
    client.send(command.encode())
    response = client.recv(1024).decode()
    print(f"Server response: {response}")
    client.close()

send_command("LIST_APPS")
