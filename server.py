import socket
import json
import psutil
import subprocess
from threading import Thread

# lay dia chi noi bo server
def layDiaChiIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # ket noi den 1 dia chi ngoai de lay ip
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

# lay danh sach dich vu dang chay
def danhSachServices():
    services = {service.name(): 'running' if service.status() == 'running' else 'stopped' 
                for service in psutil.win_service_iter()}
    return services

# lay danh sach ung dung dang chay
def danhSachApplication():
    applications = {}
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            app_name = proc.info['name']
            if app_name and app_name not in applications:
                applications[app_name] = 'running'
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return applications

# khoi dong dich vu
def khoiDongService(service_name):
    try:
        # su dung PowerShell de dung dich vu (1 so dich vu nhu Audiosrv can su dung quyen cao cap de thuc thi )
        command = f"Start-Service -Name {service_name}"
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)

        if result.returncode == 0:
            return f"Service {service_name} started."
        else:
            return f"Cannot start service {service_name}: {result.stderr.strip()}"
    except Exception as e:
        return f"Failed to start service {service_name}: {e}"

# dung dich vu
def tatService(service_name):
    try:
        # su dung PowerShell de dung dich vu (1 so dich vu nhu Audiosrv can su dung quyen cao cap de thuc thi )
        command = f"Stop-Service -Name {service_name} -Force"
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)

        if result.returncode == 0:
            return f"Service {service_name} stopped."
        else:
            return f"Cannot stop service {service_name}: {result.stderr.strip()}"
    except Exception as e:
        return f"Failed to stop service {service_name}: {e}"

# khoi dong ung dung
def khoiDongApplication(application_name):
    try:
        subprocess.Popen(application_name)
        return f"Application {application_name} started."
    except Exception as e:
        return f"Failed to start application {application_name}: {e}"

# dung ung dung
def tatApplication(application_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == application_name:
            proc.terminate()
            return f"Application {application_name} stopped."
    return f"Application {application_name} not found or not running."

# xu ly yeu cau tu client
def xuLyClient(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        if request == "danhSachServices":
            services = danhSachServices()
            response = json.dumps(services)
        elif request == "danhSachApplication":
            applications = danhSachApplication()
            response = json.dumps(applications)
        else:
            data = json.loads(request)
            name = data.get("service_name") or data.get("application_name")
            action = data["action"]

            if "service_name" in data:
                if action == "start":
                    response = khoiDongService(name)
                elif action == "stop":
                    response = tatService(name)
            elif "application_name" in data:
                if action == "start":
                    response = khoiDongApplication(name)
                elif action == "stop":
                    response = tatApplication(name)
            else:
                response = "Invalid action or target type."
                
        client_socket.send(response.encode())
    except Exception as e:
        client_socket.send(f"Error processing request: {e}".encode())
    finally:
        client_socket.close()

# khoi dong server
def khoiDongServer():
    local_ip = layDiaChiIP()
    print(f"Server đang chạy trên IP: {local_ip}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((local_ip, 12345))
    server_socket.listen(5)
    print("Server đang lắng nghe kết nối...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Kết nối từ {addr}")
        client_thread = Thread(target=xuLyClient, args=(client_socket,))
        client_thread.start()

khoiDongServer()
