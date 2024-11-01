import tkinter as tk
from tkinter import messagebox, ttk
import socket
import json
import threading
import psutil
import os

# Bien de kiem soat trang thai chay cua luong
is_running = True

# Ham tao ket noi toi server voi IP nhap tu nguoi dung
def ketNoiServer(ip):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 12345))
        return client_socket
    except Exception as e:
        messagebox.showerror("Ket noi that bai", f"Khong the ket noi toi server: {e}")
        return None

# Ham kiem tra ket noi khi nhan nut "Ket noi"
def kiemTraKetNoi():
    client_socket = ketNoiServer(ip_entry.get())
    if client_socket:
        messagebox.showinfo("Ket noi thanh cong", f"Ket noi toi server {ip_entry.get()} thanh cong")
        client_socket.close()

# Ham nhan toan bo du lieu tu server
def receive_full_data(sock):
    buffer_size = 4096
    data = b""
    while True:
        part = sock.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break
    return data.decode()

# Ham cap nhat danh sach services trong luong rieng
def capNhatServices():
    def run():
        if not is_running:  # Kiem tra neu ung dung dang dong
            return
        client_socket = ketNoiServer(ip_entry.get())
        if client_socket:
            client_socket.send(b"danhSachServices")
            data = receive_full_data(client_socket)
            client_socket.close()
            try:
                services = json.loads(data)
                hienThiDanhSach(services)
            except json.JSONDecodeError as e:
                messagebox.showerror("Loi", f"Du lieu tu server khong hop le: {e}")
            # Vo hieu hoa nut Services, kich hoat lai nut Application, doi mau nut
            service_button.config(state="disabled", bg="lightgrey")
            app_button.config(state="normal", bg="SystemButtonFace")
        else:
            messagebox.showerror("Loi", "Khong the ket noi toi server de lay danh sach services.")
    threading.Thread(target=run).start()

# Ham cap nhat danh sach applications trong luong rieng
def capNhatApplication():
    def run():
        if not is_running:  # Kiem tra neu ung dung dang dong
            return
        client_socket = ketNoiServer(ip_entry.get())
        if client_socket:
            client_socket.send(b"danhSachApplication")
            data = receive_full_data(client_socket)
            client_socket.close()
            try:
                applications = json.loads(data)
                hienThiDanhSach(applications)
            except json.JSONDecodeError as e:
                messagebox.showerror("Loi", f"Du lieu tu server khong hop le: {e}")
            app_button.config(state="disabled", bg="lightgrey")
            service_button.config(state="normal", bg="SystemButtonFace")
        else:
            messagebox.showerror("Loi", "Khong the ket noi toi server de lay danh sach applications.")
    threading.Thread(target=run).start()

# Ham cap nhat trang thai cua dich vu/ung dung
def capNhatStatusAppService(name, action):
    client_socket = ketNoiServer(ip_entry.get())
    if client_socket:
        request = json.dumps({"service_name": name, "action": action})
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        client_socket.close()
        
        # Kiem tra ket qua tra ve tu server
        if "Cannot stop service" in response:
            messagebox.showerror("Phan hoi", f"Khong the stop service {name}: Dich vu nay la can thiet hoac bi gioi han.")
        elif "Error processing request" in response or "Failed" in response:
            messagebox.showerror("Phan hoi", response)
        else:
            messagebox.showinfo("Phan hoi", response)
            # Cap nhat lai danh sach hien tai (khong thay doi giua Services va Applications)
            if service_button["state"] == "disabled":
                capNhatServices()
            elif app_button["state"] == "disabled":
                capNhatApplication()

# Ham hien thi danh sach len TreeView
def hienThiDanhSach(items):
    # Xoa tat ca item cu trong TreeView
    for row in tree.get_children():
        tree.delete(row)

    # Them item moi vao TreeView
    for item, status in items.items():
        status_text = "Run" if status == "running" else "Stop"
        tree.insert("", "end", values=(item, status_text))

# Ham xu ly su kien khi chon hang trong TreeView
def xuLyChonItem(event):
    selected_item = tree.selection()
    if selected_item:
        name, status_text = tree.item(selected_item[0], 'values')
        start_button.config(state="normal" if status_text == "Stop" else "disabled")
        stop_button.config(state="normal" if status_text == "Run" else "disabled")

# Ham bat dau dich vu
def batDauService():
    selected_item = tree.selection()[0]
    name, _ = tree.item(selected_item, 'values')
    capNhatStatusAppService(name, "start")

# Ham dung dich vu
def dungService():
    selected_item = tree.selection()[0]
    name, _ = tree.item(selected_item, 'values')
    capNhatStatusAppService(name, "stop")

# Ham dong tat ca tien trinh con
def dongTatCaTienTrinhCon():
    current_process = psutil.Process(os.getpid())
    for child in current_process.children(recursive=True):
        try:
            child.terminate()  # Dung tien trinh con
        except psutil.NoSuchProcess:
            continue
    gone, still_alive = psutil.wait_procs(current_process.children(recursive=True), timeout=3)
    for p in still_alive:
        p.kill()  # Kiem tra va dung tat ca tien trinh con

# Ham dong ung dung hoan toan khi nhan X
def on_closing():
    global is_running
    is_running = False  # Dat trang thai ung dung la khong chay
    dongTatCaTienTrinhCon()  # Goi ham de dong tat ca tien trinh con
    print("Dong ung dung hoan toan")
    root.destroy()  # Dam bao cua so chinh bi dong hoan toan

# Giao dien chinh
root = tk.Tk()
root.title("Remote Controller")

# Gan su kien dong cua so cho ham on_closing
root.protocol("WM_DELETE_WINDOW", on_closing)

# Frame chua o nhap IP va nut ket noi
top_frame = tk.Frame(root)
top_frame.pack(anchor="w", pady=5)

ip_entry = tk.Entry(top_frame, width=30)
ip_entry.grid(row=0, column=0, padx=5)
ip_entry.insert(0, "Nhap IP server")

connect_button = tk.Button(top_frame, text="Ket noi", command=kiemTraKetNoi)
connect_button.grid(row=0, column=1, padx=5)

# Frame chua cac nut Application, Services, Start, Stop
button_frame = tk.Frame(root)
button_frame.pack(anchor="w", pady=5)

app_button = tk.Button(button_frame, text="Application", command=capNhatApplication)
app_button.grid(row=0, column=0, padx=5)

service_button = tk.Button(button_frame, text="Services", command=capNhatServices)
service_button.grid(row=0, column=1, padx=5)

start_button = tk.Button(button_frame, text="Start", command=batDauService, state="disabled")
start_button.grid(row=0, column=2, padx=5)

stop_button = tk.Button(button_frame, text="Stop", command=dungService, state="disabled")
stop_button.grid(row=0, column=3, padx=5)

# TreeView hien thi danh sach
tree = ttk.Treeview(root, columns=("Name", "Status"), show="headings", height=15)
tree.heading("Name", text="Name")
tree.heading("Status", text="Status")
tree.column("Name", width=200)
tree.column("Status", width=100)
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Them su kien cho TreeView de bat hanh dong khi chon item
tree.bind("<<TreeviewSelect>>", xuLyChonItem)

root.mainloop()
