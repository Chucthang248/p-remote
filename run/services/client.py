import tkinter as tk
from tkinter import messagebox
import socket
import json

# Kết nối tới server, xử lý khi không kết nối được
def connect_to_server():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("192.168.11.130", 12345))  # Thay SERVER_IP bằng IP của server
        return client_socket
    except Exception as e:
        print(f"Không thể kết nối tới server: {e}")
        return None

# Hàm gửi yêu cầu dừng hoặc khởi động service tới server
def control_service(service_name, action):
    if client_socket:
        request = {"service_name": service_name, "action": action}
        client_socket.send(json.dumps(request).encode())
        response = client_socket.recv(1024).decode()
        messagebox.showinfo("Response", response)
        update_services()
    else:
        messagebox.showwarning("Warning", "Không kết nối được tới server, không thể thực hiện hành động.")

# Hàm cập nhật danh sách services
def update_services():
    if client_socket:
        client_socket.send(b"LIST_SERVICES")
        data = client_socket.recv(4096).decode()
        services = json.loads(data)
    else:
        # Dữ liệu mẫu khi không kết nối được với server
        services = {
            "SampleService1": "running",
            "SampleService2": "stopped",
            "SampleService3": "running",
            "SampleService4": "running",
            "SampleService5": "stopped"
        }
    
    # Xóa các widget cũ trong khung canvas
    for widget in services_frame.winfo_children():
        widget.destroy()
    
    # Hiển thị danh sách services
    for service, status in services.items():
        frame = tk.Frame(services_frame)
        frame.pack(fill="x")
        
        service_label = tk.Label(frame, text=service, width=20)
        service_label.pack(side="left")
        
        start_button = tk.Button(frame, text="Start", command=lambda s=service: control_service(s, "start"))
        stop_button = tk.Button(frame, text="Stop", command=lambda s=service: control_service(s, "stop"))
        
        if status == "running":
            start_button.config(state="disabled")
        else:
            stop_button.config(state="disabled")
        
        start_button.pack(side="left")
        stop_button.pack(side="left")

# Tạo giao diện client
client_socket = connect_to_server()
root = tk.Tk()
root.title("Remote Service Controller")

# Tạo canvas cho khung dịch vụ cuộn
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Đặt canvas và scrollbar vào cửa sổ
scrollbar.pack(side="right", fill="y")
canvas.pack(fill="both", expand=True)

# Khung cho danh sách services bên trong canvas
services_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=services_frame, anchor="nw")

# Cập nhật kích thước canvas khi nội dung thay đổi
services_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

update_services()

root.mainloop()
