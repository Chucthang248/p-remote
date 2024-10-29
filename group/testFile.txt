import socket
import winreg
import subprocess
import psutil

# Kết nối với client
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 49691))
server_socket.listen(5)

print("Server dang cho ket noi...")

# Hàm list_processes liệt kê các ứng dụng đang chạy có đuôi exe, bat, và cmd.exe
def list_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Lấy tên tiến trình
            process_name = proc.info['name']
            # Chỉ thêm vào danh sách nếu tên tiến trình không rỗng
            if process_name:  
                # Chỉ lấy các ứng dụng có đuôi .exe, .bat hoặc cmd.exe
                if process_name.endswith('.exe') or process_name.endswith('.bat') or process_name == 'cmd.exe':
                    processes.append(f"PID: {proc.info['pid']} - Name: {process_name}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Bỏ qua các tiến trình mà không thể truy cập thông tin
            continue
    return "\n".join(processes)

# Hàm find_application_path tìm đường dẫn của ứng dụng
def find_application_path(app_name):
    try:
        # Mở khóa HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
        # Lặp qua tất cả các khóa con để tìm ứng dụng
        index = 0
        while True:
            try:
                sub_key_name = winreg.EnumKey(registry_key, index)
                app_key = winreg.OpenKey(registry_key, sub_key_name)
                # Lấy đường dẫn đến ứng dụng
                app_path, _ = winreg.QueryValueEx(app_key, "")
                # Kiểm tra tên ứng dụng và trả về đường dẫn nếu tìm thấy
                if app_name.lower() in sub_key_name.lower():
                    return app_path  
                index += 1
            # Kết thúc khi không còn khóa con nào
            except OSError:
                break  
        # Trả về None nếu không tìm thấy ứng dụng
        winreg.CloseKey(registry_key)
        return None
    except Exception as e:
        print(f"Error accessing registry: {e}")
        return None
    
# Hàm open_application để mở ứng dụng
def open_application(app_name):
    # Tìm đường dẫn từ hàm find_application_path
    app_path = find_application_path(app_name)
    # Mở ứng dụng và trả về message
    if app_path:
        subprocess.Popen(app_path, shell=True)
        return f"Application '{app_name}' started successfully."
    else:
        return f"Application '{app_name}' not found in the registry."
    
# Hàm open_application để đóng ứng dụng
def close_application(app_name):
    try:
        # Thêm đuôi exe vào tên của ứng dụng
        if not app_name.lower().endswith('.exe'):
            app_name += '.exe'
        closed_processes = 0
        # Tìm tất cả các ứng dụng có tên từ người dùng cung cấp, đóng tất cả các tiến trình và trả về message
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == app_name.lower():
                proc.terminate()
                closed_processes += 1
        if closed_processes > 0:
            return f"Closed {closed_processes} instances of '{app_name}' successfully."
        else:
            return f"Application '{app_name}' not found."
    except Exception as e:
        return f"Failed to close application '{app_name}': {e}"
    
# Vòng lặp lấy socket từ client và địa chỉ từ client
while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    # Nhận dữ liệu từ client và giải mã. Dữ liệu có kích thước tối đa 1024
    data = client_socket.recv(1024).decode()
    if data == "list":
        # Nếu dữ liệu là list thì gọi hàm list_processes và gán kết quả vào response
        response = list_processes()
    elif data.startswith("open:"):
        # Nếu dữ liệu bắt đầu bằng open, gọi hàm open_application
        # Tham số : app_name tên application nhận từ client
        # Kết quả trả về gán vào response
        app_name = data.split(":", 1)[1]
        response = open_application(app_name)
    elif data.startswith("close:"):
        # Nếu dữ liệu bắt đầu bằng close, gọi hàm close_application
        # Tham số : app_name tên application nhận từ client
        # Kết quả trả về gán vào response
        app_name = data.split(":", 1)[1]
        response = close_application(app_name)
    else:
        # Gán invalid command vào response nếu không có data phù hợp
        response = "Invalid command."
    # Gửi phản hồi về client và đóng kết nối
    client_socket.sendall(response.encode())
    client_socket.close()