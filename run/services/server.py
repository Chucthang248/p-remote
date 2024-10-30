import socket
import psutil
import json
import subprocess

# Tạo server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(5)

# In ra địa chỉ IP của server
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
print(f"Địa chỉ IP của server: {server_ip}")

# Xử lý yêu cầu từ client
def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break

        if request == "LIST_SERVICES":
            services = {proc.name(): "running" if proc.is_running() else "stopped" for proc in psutil.process_iter(['name'])}
            client_socket.send(json.dumps(services).encode())
        
        else:
            data = json.loads(request)
            service_name = data["service_name"]
            action = data["action"]
            
            if action == "start":
                try:
                    subprocess.Popen(service_name)  # Bật service
                    client_socket.send(f"{service_name} đã được khởi động".encode())
                except Exception as e:
                    client_socket.send(f"Không thể khởi động {service_name}: {e}".encode())

            elif action == "stop":
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == service_name:
                        proc.terminate()
                        client_socket.send(f"{service_name} đã bị dừng".encode())
                        break
                else:
                    client_socket.send(f"{service_name} không chạy".encode())

while True:
    client, addr = server_socket.accept()
    print(f"Kết nối từ {addr}")
    handle_client(client)
    client.close()
