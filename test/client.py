import socket
import tkinter as tk
from tkinter import ttk
import logging
from ip import get_local_ip

# Cấu hình logging, lưu log vào file 'client.log' và ghi ở mức DEBUG
logging.basicConfig(filename='log/client.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Hàm send_command kết nối với server và gửi command
def send_command(command):
    try:
        #server_ip = get_local_ip()
        server_ip = '192.168.11.130'
        logging.debug(f"IP: {server_ip}")
        logging.debug(f"dang ket noi: {command}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, 49691))
            client_socket.sendall(command.encode())
            response = client_socket.recv(1024).decode()
        return response
    except Exception as e:
        logging.error(f"loi khi gui toi server: {str(e)}")
        return f"Error: {str(e)}"

# Hàm fetch_process_applications_list để gửi và in ra các ứng dụng đang chạy. Các ứng dụng có đuôi exe, bat, cmd.exe
def fetch_process_applications_list():
    logging.debug("bat dau cap nhat danh sach")
    try:
        processes = send_command("list").split("\n")
        process_list.delete(0, tk.END)  # Xóa danh sách cũ trước khi cập nhật
        for process in processes:
            # Kiểm tra và thêm ứng dụng vào danh sách hiển thị
            if process:
                if (process.endswith('.exe') or process.endswith('.bat') or 'cmd.exe' in process):
                    process_list.insert(tk.END, process)
        logging.debug("cap nhat danh sach hoan tat")
    except Exception as e:
        logging.error(f"loi cap nhat: {str(e)}")


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
