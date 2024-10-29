import socket
import tkinter as tk
from tkinter import ttk

# Hàm send_command kết nối với server và gửi command
def send_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(('192.168.141.128', 49691))
            client_socket.sendall(command.encode())
            response = client_socket.recv(1024).decode()
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Hàm fetch_process_applications_list để gửi và in ra các ứng dụng đang chạy. Các ứng dụng có đuôi exe, bat, cmd.exe
def fetch_process_applications_list():
    processes = send_command("list").split("\n")
    # Xóa danh sách cũ trước khi cập nhật
    process_list.delete(0, tk.END)
    for process in processes:
        # Kiểm tra nếu process không rỗng và ứng dụng có đuôi exe, bat, cmd.exe và thêm ứng dụng vào danh sách hiển thị
        if process:
            if (process.endswith('.exe') or process.endswith('.bat') or 'cmd.exe' in process):
                process_list.insert(tk.END, process)


# Hàm open_application để mở ứng dụng
# app_name : tên ứng dụng nhập từ người dùng
def open_application():
    app_name = app_entry.get()
    # Gửi lệnh mở đến server và hiển thị kết quả
    response = send_command(f"open:{app_name}")
    result_label.config(text=response)

# Hàm stop_application để đóng ứng dụng
# app_name : tên ứng dụng nhập từ người dùng
def stop_application():
    app_name = app_entry.get()
    # Gửi lệnh đóng đến server và hiển thị kết quả
    response = send_command(f"close:{app_name}")
    result_label.config(text=response)

# Thiết lập GUI
root = tk.Tk()
root.title("Server Process Controller")

# Bảng hiển thị danh sách các ứng dụng đang chạy
# Chiều rộng của bảng chứa được 60 ký tự, chiều cao chứ được 30 dòng, và padding của bảng là 5
process_list = tk.Listbox(root, width=60, height=30)
process_list.pack(pady=5)

# Nút để cập nhật các dứng dụng đang chạy
ttk.Button(root, text="Update Application List", command=fetch_process_applications_list).pack(pady=5)

# Ô nhập liệu, người dùng nhập tên ứng dụng để mở/đóng
app_entry = ttk.Entry(root, width=40)
app_entry.pack(pady=5)

# Nút mở dúng dụng
ttk.Button(root, text="Open Application", command=open_application).pack(pady=5)

# Nút đóng dúng dụng
ttk.Button(root, text="Close Application", command=stop_application).pack(pady=5)

# Kết quả trả về từ các commands của server
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

# Mở giao diện GUI
root.mainloop()
